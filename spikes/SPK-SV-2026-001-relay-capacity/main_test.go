package main

import (
	"sync"
	"testing"
	"time"
)

func TestProtectionEnforcesConcurrencyLimit(t *testing.T) {
	guard := &protection{concurrency: 2, rateLimit: 100, rateWindow: time.Minute}
	if !guard.acquire(time.Unix(0, 0)) || !guard.acquire(time.Unix(0, 1)) {
		t.Fatal("first two attempts should be admitted")
	}
	if guard.acquire(time.Unix(0, 2)) {
		t.Fatal("third concurrent attempt should be rejected")
	}
	guard.release()
	if !guard.acquire(time.Unix(0, 3)) {
		t.Fatal("attempt should be admitted after release")
	}
}

func TestProtectionEnforcesRateLimit(t *testing.T) {
	guard := &protection{concurrency: 100, rateLimit: 3, rateWindow: time.Minute}
	for i := 0; i < 3; i++ {
		if !guard.acquire(time.Unix(0, int64(i))) {
			t.Fatalf("attempt %d should be admitted", i)
		}
		guard.release()
	}
	if guard.acquire(time.Unix(0, 4)) {
		t.Fatal("fourth attempt in window should be rejected")
	}
	if !guard.acquire(time.Unix(61, 0)) {
		t.Fatal("attempt after window should be admitted")
	}
}

func TestPairingLimiterEnforcesWindow(t *testing.T) {
	l := newPairingLimiter(5, time.Minute)
	for i := 0; i < 5; i++ {
		if !l.allow("p1", time.Unix(0, int64(i))) {
			t.Fatalf("attempt %d should be admitted", i)
		}
	}
	if l.allow("p1", time.Unix(0, 6)) {
		t.Fatal("sixth attempt in window should be rejected")
	}
	if !l.allow("p2", time.Unix(0, 6)) {
		t.Fatal("independent pairing key should be admitted")
	}
	if !l.allow("p1", time.Unix(61, 0)) {
		t.Fatal("attempt after window should be admitted")
	}
}

func TestPairingLimiterDisabled(t *testing.T) {
	l := newPairingLimiter(0, time.Minute)
	for i := 0; i < 100; i++ {
		if !l.allow("p1", time.Unix(0, int64(i))) {
			t.Fatal("disabled limiter must admit everything")
		}
	}
	if got := l.tracked(); got != 0 {
		t.Fatalf("disabled limiter must not track keys, got %d", got)
	}
}

func TestPercentileMs(t *testing.T) {
	if got := percentileMs(nil, 0.95); got != 0 {
		t.Fatalf("empty input must yield 0, got %v", got)
	}
	latencies := make([]time.Duration, 0, 100)
	for i := 1; i <= 100; i++ {
		latencies = append(latencies, time.Duration(i)*time.Millisecond)
	}
	if got := percentileMs(latencies, 0.50); got != 50 {
		t.Fatalf("p50 of 1..100ms should be 50, got %v", got)
	}
	if got := percentileMs(latencies, 0.95); got != 95 {
		t.Fatalf("p95 of 1..100ms should be 95, got %v", got)
	}
	if got := percentileMs(latencies, 0.99); got != 99 {
		t.Fatalf("p99 of 1..100ms should be 99, got %v", got)
	}
}

func TestProtectionConcurrentAccounting(t *testing.T) {
	guard := &protection{concurrency: 10, rateLimit: 1000, rateWindow: time.Minute}
	var wg sync.WaitGroup
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			if guard.acquire(time.Unix(0, int64(i))) {
				guard.release()
			}
		}(i)
	}
	wg.Wait()
	if got := guard.stats()["active"]; got != 0 {
		t.Fatalf("active count must return to zero, got %v", got)
	}
}
