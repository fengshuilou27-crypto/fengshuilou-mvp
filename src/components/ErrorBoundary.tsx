import { Component, type ReactNode } from 'react'

interface Props { children: ReactNode }
interface State { error: Error | null }

// 全局錯誤邊界：任何渲染錯誤（如 hook 順序、空值訪問）不再導致整頁白屏，
// 而是顯示錯誤信息與重載按鈕，便於診斷
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: unknown) {
    console.error('[ErrorBoundary]', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen bg-[#0a0f1c] text-slate-200 flex items-center justify-center p-6">
          <div className="max-w-lg rounded-xl border border-rose-500/40 bg-rose-500/10 p-6">
            <h1 className="text-lg font-bold text-rose-300 mb-2">頁面渲染出錯（已攔截，未白屏）</h1>
            <p className="text-xs text-slate-300 mb-3 break-all font-mono">
              {this.state.error.message}
            </p>
            <button
              onClick={() => location.reload()}
              className="px-4 py-2 rounded-md bg-rose-500/20 border border-rose-500/40 text-rose-200 text-sm hover:bg-rose-500/30"
            >
              重新載入頁面
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
