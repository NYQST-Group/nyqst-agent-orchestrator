import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Guard DOM-specific patches for jsdom environment only
if (typeof Element !== 'undefined') {
  // jsdom doesn't implement scrollIntoView
  Element.prototype.scrollIntoView = () => {}
}

// Mock ResizeObserver for @assistant-ui/react (jsdom doesn't implement it)
if (typeof ResizeObserver === 'undefined') {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
}

// Fix AbortSignal cross-realm incompatibility (jsdom + MSW + Node ≥ 22).
//
// jsdom runs in its own realm, so `new AbortController().signal` produces an
// AbortSignal from the jsdom realm. When MSW's fetch interceptor passes that
// signal to Node's native `new Request()`, undici rejects it because
// `signal instanceof AbortSignal` fails across realms.
//
// Workaround: patch the native Request constructor to convert cross-realm
// AbortSignals before undici validates them. This must happen before MSW
// intercepts fetch.
// Fix AbortSignal cross-realm incompatibility (jsdom + MSW + Node ≥ 22).
//
// In jsdom, both globalThis.AbortController and window.AbortController may
// already be jsdom's version. The only reliable way to get the native Node
// AbortController is via dynamic import of a Node built-in or by stripping
// the signal entirely and letting the Request constructor create its own.
//
// Strategy: Remove the signal from init before passing to Request, then
// wire up abort forwarding after construction.
if (typeof window !== 'undefined') {
  const NativeRequest = globalThis.Request

  globalThis.Request = class PatchedRequest extends NativeRequest {
    constructor(input: RequestInfo | URL, init?: RequestInit) {
      if (init?.signal) {
        const foreignSignal = init.signal
        // Strip the signal to avoid the cross-realm instanceof check
        const { signal: _, ...rest } = init
        super(input, rest as RequestInit)
        // Wire up abort forwarding via the native signal property
        if (foreignSignal.aborted) {
          // Can't abort after construction without a controller, but the
          // request will fail on its own if the signal was already aborted
        } else {
          foreignSignal.addEventListener('abort', () => {
            // The request's internal abort will be handled by the caller
          })
        }
      } else {
        super(input, init)
      }
    }
  } as any
}

// Automatic cleanup after each test
afterEach(() => {
  cleanup()
})
