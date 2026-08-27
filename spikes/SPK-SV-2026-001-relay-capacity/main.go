package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"math"
	"net/http"
	"os"
	"runtime"
	"sort"
	"sync"
	"sync/atomic"
	"time"

	"github.com/coder/websocket"
)

type protection struct {
	mu          sync.Mutex
	active      int
	concurrency int
	rateLimit   int
	rateWindow  time.Duration
	attempts    []time.Time
	accepted    atomic.Int64
	rejected    atomic.Int64
}

func (p *protection) acquire(now time.Time) bool {
	p.mu.Lock()
	defer p.mu.Unlock()
	cutoff := now.Add(-p.rateWindow)
	keep := p.attempts[:0]
	for _, attempt := range p.attempts {
		if attempt.After(cutoff) {
			keep = append(keep, attempt)
		}
	}
	p.attempts = append(keep, now)
	if len(p.attempts) > p.rateLimit || p.active >= p.concurrency {
		p.rejected.Add(1)
		return false
	}
	p.active++
	p.accepted.Add(1)
	return true
}

func (p *protection) release() {
	p.mu.Lock()
	p.active--
	p.mu.Unlock()
}

func (p *protection) stats() map[string]any {
	p.mu.Lock()
	defer p.mu.Unlock()
	return map[string]any{
		"active":              p.active,
		"attempts_in_window":  len(p.attempts),
		"accepted_handshakes": p.accepted.Load(),
		"rejected_handshakes": p.rejected.Load(),
		"concurrency_limit":   p.concurrency,
		"rate_limit":          p.rateLimit,
		"rate_window_seconds": p.rateWindow.Seconds(),
	}
}

// pairingLimiter 是独立于全局保护层的 pairing 级滑动窗口限流器。
type pairingLimiter struct {
	mu       sync.Mutex
	limit    int
	window   time.Duration
	attempts map[string][]time.Time
}

func newPairingLimiter(limit int, window time.Duration) *pairingLimiter {
	return &pairingLimiter{limit: limit, window: window, attempts: map[string][]time.Time{}}
}

func (l *pairingLimiter) allow(key string, now time.Time) bool {
	if l.limit <= 0 || key == "" {
		return true
	}
	l.mu.Lock()
	defer l.mu.Unlock()
	cutoff := now.Add(-l.window)
	keep := l.attempts[key][:0]
	for _, at := range l.attempts[key] {
		if at.After(cutoff) {
			keep = append(keep, at)
		}
	}
	keep = append(keep, now)
	l.attempts[key] = keep
	return len(keep) <= l.limit
}

func (l *pairingLimiter) tracked() int {
	l.mu.Lock()
	defer l.mu.Unlock()
	return len(l.attempts)
}

type serverCounters struct {
	echoedMessages atomic.Int64
	pushedBytes    atomic.Int64
}

func serveSession(ctx context.Context, conn *websocket.Conn, echo bool, pushInterval time.Duration, pushSize int, counters *serverCounters) {
	if pushInterval > 0 && pushSize > 0 {
		payload := make([]byte, pushSize)
		go func() {
			ticker := time.NewTicker(pushInterval)
			defer ticker.Stop()
			for {
				select {
				case <-ctx.Done():
					return
				case <-ticker.C:
					// 慢消费者场景下此写会阻塞:每条连接最多一个被阻塞的写 goroutine,
					// 无内部无界队列,背压直接体现在 goroutine 数与 RSS 上。
					if err := conn.Write(ctx, websocket.MessageBinary, payload); err != nil {
						return
					}
					counters.pushedBytes.Add(int64(len(payload)))
				}
			}
		}()
	}
	for {
		typ, data, err := conn.Read(ctx)
		if err != nil {
			return
		}
		if echo {
			if err := conn.Write(ctx, typ, data); err != nil {
				return
			}
			counters.echoedMessages.Add(1)
		}
	}
}

func runServer(addr string, concurrency, rateLimit int, rateWindow, handshakeHold, sessionHold time.Duration, pairingLimit int, pairingWindow time.Duration, echo bool, pushInterval time.Duration, pushSize int) error {
	guard := &protection{
		concurrency: concurrency,
		rateLimit:   rateLimit,
		rateWindow:  rateWindow,
	}
	pairings := newPairingLimiter(pairingLimit, pairingWindow)
	counters := &serverCounters{}
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusNoContent)
	})
	mux.HandleFunc("/stats", func(w http.ResponseWriter, _ *http.Request) {
		stats := guard.stats()
		stats["goroutines"] = runtime.NumGoroutine()
		stats["tracked_pairings"] = pairings.tracked()
		stats["echoed_messages"] = counters.echoedMessages.Load()
		stats["pushed_bytes"] = counters.pushedBytes.Load()
		stats["pairing_rate_limit"] = pairingLimit
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(stats)
	})
	mux.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
		if !guard.acquire(time.Now()) {
			w.Header().Set("Content-Type", "text/plain; charset=utf-8")
			w.WriteHeader(http.StatusTooManyRequests)
			_, _ = w.Write([]byte("RATE_LIMITED"))
			return
		}
		defer guard.release()
		if !pairings.allow(r.URL.Query().Get("pairing"), time.Now()) {
			w.Header().Set("Content-Type", "text/plain; charset=utf-8")
			w.WriteHeader(http.StatusTooManyRequests)
			_, _ = w.Write([]byte("RATE_LIMITED"))
			return
		}
		if handshakeHold > 0 {
			time.Sleep(handshakeHold)
		}
		conn, err := websocket.Accept(w, r, &websocket.AcceptOptions{InsecureSkipVerify: true})
		if err != nil {
			return
		}
		defer conn.Close(websocket.StatusNormalClosure, "")
		if echo || pushInterval > 0 {
			// Spike 专用:echo 模式放宽读上限以覆盖消息大小阶梯,生产实现必须按契约设定上限。
			conn.SetReadLimit(4 << 20)
			serveSession(r.Context(), conn, echo, pushInterval, pushSize, counters)
			return
		}
		if sessionHold <= 0 {
			return
		}
		select {
		case <-r.Context().Done():
		case <-time.After(sessionHold):
		}
	})
	server := &http.Server{Addr: addr, Handler: mux, ReadHeaderTimeout: 5 * time.Second}
	log.Printf("synthetic relay listening on %s", addr)
	return server.ListenAndServe()
}

type loadOptions struct {
	target        string
	attempts      int
	parallel      int
	size          int           // echo 载荷字节数;>0 时拨号后发送并等待回显
	read          bool          // false = 慢消费者:拨号后不读,仅持有
	hold          time.Duration // 拨号后持有时长
	pairingKey    string        // pairing id 前缀;空则不携带
	pairingFanout int           // >1 时按 pairingKey-i 轮转分散到多个 id
}

type loadResult struct {
	Attempts      int           `json:"attempts"`
	Parallel      int           `json:"parallel"`
	Accepted      int64         `json:"accepted"`
	RateLimited   int64         `json:"rate_limited"`
	OtherFailures int64         `json:"other_failures"`
	Elapsed       time.Duration `json:"elapsed"`
	P50Ms         float64       `json:"p50_ms,omitempty"`
	P95Ms         float64       `json:"p95_ms,omitempty"`
	P99Ms         float64       `json:"p99_ms,omitempty"`
	Size          int           `json:"size,omitempty"`
	Target        string        `json:"target"`
}

func percentileMs(latencies []time.Duration, q float64) float64 {
	if len(latencies) == 0 {
		return 0
	}
	sorted := make([]time.Duration, len(latencies))
	copy(sorted, latencies)
	sort.Slice(sorted, func(i, j int) bool { return sorted[i] < sorted[j] })
	idx := int(math.Ceil(q * float64(len(sorted))))
	if idx < 1 {
		idx = 1
	}
	if idx > len(sorted) {
		idx = len(sorted)
	}
	return float64(sorted[idx-1]) / float64(time.Millisecond)
}

func runLoad(opts loadOptions) loadResult {
	if opts.parallel < 1 {
		opts.parallel = 1
	}
	start := time.Now()
	jobs := make(chan int)
	var accepted, limited, other atomic.Int64
	latCh := make(chan time.Duration, opts.attempts)
	var wg sync.WaitGroup
	for i := 0; i < opts.parallel; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for n := range jobs {
				target := opts.target
				if opts.pairingKey != "" {
					id := opts.pairingKey
					if opts.pairingFanout > 1 {
						id = fmt.Sprintf("%s-%d", opts.pairingKey, n%opts.pairingFanout)
					}
					target = fmt.Sprintf("%s?pairing=%s", opts.target, id)
				}
				attemptStart := time.Now()
				ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
				conn, resp, err := websocket.Dial(ctx, target, nil)
				if err != nil {
					cancel()
					if resp != nil && resp.StatusCode == http.StatusTooManyRequests {
						limited.Add(1)
					} else {
						other.Add(1)
					}
					continue
				}
				if opts.size > 0 {
					conn.SetReadLimit(int64(opts.size)*2 + 1024)
					payload := make([]byte, opts.size)
					if err := conn.Write(ctx, websocket.MessageBinary, payload); err == nil {
						_, _, err = conn.Read(ctx)
					}
					if err != nil {
						cancel()
						_ = conn.Close(websocket.StatusInternalError, "")
						other.Add(1)
						continue
					}
				}
				if !opts.read || opts.hold > 0 {
					select {
					case <-ctx.Done():
					case <-time.After(opts.hold):
					}
				}
				cancel()
				_ = conn.Close(websocket.StatusNormalClosure, "")
				accepted.Add(1)
				latCh <- time.Since(attemptStart)
			}
		}()
	}
	for i := 0; i < opts.attempts; i++ {
		jobs <- i
	}
	close(jobs)
	wg.Wait()
	close(latCh)
	latencies := make([]time.Duration, 0, opts.attempts)
	for d := range latCh {
		latencies = append(latencies, d)
	}
	return loadResult{
		Attempts:      opts.attempts,
		Parallel:      opts.parallel,
		Accepted:      accepted.Load(),
		RateLimited:   limited.Load(),
		OtherFailures: other.Load(),
		Elapsed:       time.Since(start),
		P50Ms:         percentileMs(latencies, 0.50),
		P95Ms:         percentileMs(latencies, 0.95),
		P99Ms:         percentileMs(latencies, 0.99),
		Size:          opts.size,
		Target:        opts.target,
	}
}

func main() {
	mode := flag.String("mode", "server", "server or load")
	addr := flag.String("addr", "127.0.0.1:18081", "server listen address")
	target := flag.String("target", "ws://127.0.0.1:18081/ws", "websocket target")
	attempts := flag.Int("attempts", 1, "load attempts")
	parallel := flag.Int("parallel", 1, "load workers")
	concurrency := flag.Int("concurrency", 100, "global concurrent handshake limit")
	rateLimit := flag.Int("rate-limit", 300, "global handshake attempts per window")
	rateWindow := flag.Duration("rate-window", 60*time.Second, "global rate window")
	hold := flag.Duration("hold", 0, "synthetic handshake hold")
	sessionHold := flag.Duration("session-hold", 10*time.Millisecond, "synthetic post-handshake session hold")
	pairingRate := flag.Int("pairing-rate", 0, "per-pairing handshake attempts per window (0=off)")
	pairingWindow := flag.Duration("pairing-window", 60*time.Second, "per-pairing rate window")
	echo := flag.Bool("echo", false, "server echoes messages back")
	pushInterval := flag.Duration("push-interval", 0, "server push interval per connection (0=off)")
	pushSize := flag.Int("push-size", 0, "server push payload bytes per message")
	size := flag.Int("size", 0, "load echo payload bytes (requires server -echo)")
	read := flag.Bool("read", true, "load reads after dial (false = slow consumer)")
	clientHold := flag.Duration("client-hold", 0, "load holds connection after dial")
	pairingKey := flag.String("pairing-key", "", "load pairing id prefix")
	pairingFanout := flag.Int("pairing-fanout", 1, "spread load across N pairing ids")
	flag.Parse()

	switch *mode {
	case "server":
		if err := runServer(*addr, *concurrency, *rateLimit, *rateWindow, *hold, *sessionHold, *pairingRate, *pairingWindow, *echo, *pushInterval, *pushSize); err != nil && err != http.ErrServerClosed {
			log.Fatal(err)
		}
	case "load":
		result := runLoad(loadOptions{
			target:        *target,
			attempts:      *attempts,
			parallel:      *parallel,
			size:          *size,
			read:          *read,
			hold:          *clientHold,
			pairingKey:    *pairingKey,
			pairingFanout: *pairingFanout,
		})
		if err := json.NewEncoder(os.Stdout).Encode(result); err != nil {
			log.Fatal(err)
		}
	default:
		fmt.Fprintln(os.Stderr, "mode must be server or load")
		os.Exit(2)
	}
}
