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
