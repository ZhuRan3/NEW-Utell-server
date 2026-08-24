package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
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

func runServer(addr string, concurrency, rateLimit int, rateWindow, handshakeHold, sessionHold time.Duration) error {
	guard := &protection{
		concurrency: concurrency,
		rateLimit:   rateLimit,
		rateWindow:  rateWindow,
	}
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusNoContent)
	})
	mux.HandleFunc("/stats", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(guard.stats())
	})
	mux.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
		if !guard.acquire(time.Now()) {
			w.Header().Set("Content-Type", "text/plain; charset=utf-8")
			w.WriteHeader(http.StatusTooManyRequests)
			_, _ = w.Write([]byte("RATE_LIMITED"))
			return
		}
		defer guard.release()
		if handshakeHold > 0 {
			time.Sleep(handshakeHold)
		}
		conn, err := websocket.Accept(w, r, &websocket.AcceptOptions{InsecureSkipVerify: true})
		if err != nil {
			return
		}
		defer conn.Close(websocket.StatusNormalClosure, "")
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

type loadResult struct {
	Attempts      int           `json:"attempts"`
	Parallel      int           `json:"parallel"`
	Accepted      int64         `json:"accepted"`
	RateLimited   int64         `json:"rate_limited"`
	OtherFailures int64         `json:"other_failures"`
	Elapsed       time.Duration `json:"elapsed"`
	Target        string        `json:"target"`
}

func runLoad(target string, attempts, parallel int) loadResult {
	if parallel < 1 {
		parallel = 1
	}
	start := time.Now()
	jobs := make(chan struct{})
	var accepted, limited, other atomic.Int64
	var wg sync.WaitGroup
	for i := 0; i < parallel; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for range jobs {
				ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
				conn, resp, err := websocket.Dial(ctx, target, nil)
				cancel()
				if err == nil {
					_ = conn.Close(websocket.StatusNormalClosure, "")
					accepted.Add(1)
					continue
				}
				if resp != nil && resp.StatusCode == http.StatusTooManyRequests {
					limited.Add(1)
				} else {
					other.Add(1)
				}
			}
		}()
	}
	for i := 0; i < attempts; i++ {
		jobs <- struct{}{}
	}
	close(jobs)
	wg.Wait()
	return loadResult{
		Attempts:      attempts,
		Parallel:      parallel,
		Accepted:      accepted.Load(),
		RateLimited:   limited.Load(),
		OtherFailures: other.Load(),
		Elapsed:       time.Since(start),
		Target:        target,
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
	flag.Parse()

	switch *mode {
	case "server":
		if err := runServer(*addr, *concurrency, *rateLimit, *rateWindow, *hold, *sessionHold); err != nil && err != http.ErrServerClosed {
			log.Fatal(err)
		}
	case "load":
		result := runLoad(*target, *attempts, *parallel)
		if err := json.NewEncoder(os.Stdout).Encode(result); err != nil {
			log.Fatal(err)
		}
	default:
		fmt.Fprintln(os.Stderr, "mode must be server or load")
		os.Exit(2)
	}
}
