'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="flex flex-col items-center justify-center p-4 rounded-lg border border-destructive/20 bg-destructive/5 text-destructive">
            <h2 className="text-sm font-semibold mb-1">Rendering Error</h2>
            <p className="text-xs">Something went wrong while displaying this content.</p>
          </div>
        )
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
