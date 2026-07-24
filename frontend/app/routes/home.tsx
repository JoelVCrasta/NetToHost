import type { Route } from "./+types/home"
import { Link } from "react-router"
import {
  Cpu,
  ShieldAlert,
  Zap,
  Server,
  ArrowRight,
  Terminal,
  CheckCircle2,
  Sliders,
  Wrench,
  Activity,
  Layers,
} from "lucide-react"

export function meta({}: Route.MetaArgs) {
  return [
    { title: "NetToHost - AI Agent for Remote Services & Tools" },
    {
      name: "description",
      content:
        "Manage and execute remote tools, services, and infrastructure with an intelligent AI agent.",
    },
  ]
}

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Header Navigation */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-linear-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight bg-linear-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              NetToHost
            </span>
          </div>

          <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-300">
            <a
              href="#capabilities"
              className="hover:text-indigo-400 transition-colors"
            >
              Capabilities
            </a>
            <a
              href="#capabilities"
              className="hover:text-indigo-400 transition-colors"
            >
              Safety Controls
            </a>
          </nav>

          <div className="flex items-center space-x-4">
            <Link
              to="/signin"
              className="text-sm font-semibold text-slate-300 hover:text-white px-3 py-2 transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/dashboard"
              className="inline-flex items-center justify-center px-4 py-2 rounded-lg text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-500 transition-all shadow-md shadow-indigo-600/30 hover:shadow-indigo-500/40"
            >
              Launch Platform
              <ArrowRight className="w-4 h-4 ml-1.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="relative pt-24 pb-20 overflow-hidden">
          {/* Ambient Lighting Gradients */}
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-indigo-600/15 rounded-full blur-[140px] pointer-events-none" />
          <div className="absolute top-1/3 left-1/3 w-[300px] h-[300px] bg-violet-600/10 rounded-full blur-[100px] pointer-events-none" />

          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
            <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-indigo-950/60 border border-indigo-800/50 text-indigo-300 text-xs font-semibold mb-8 backdrop-blur-sm">
              <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>AI Agent Platform for Remote Infrastructure</span>
            </div>

            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight max-w-4xl mx-auto leading-none text-slate-100">
              Your Autonomous AI Agent for{" "}
              <span className="bg-linear-to-r from-indigo-400 via-violet-400 to-indigo-300 bg-clip-text text-transparent">
                Remote Services & Tools
              </span>
            </h1>

            <p className="mt-6 text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed font-normal">
              Connect remote host machines, execute system commands, and manage
              host tools through an intelligent, safe AI workspace.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/dashboard"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl text-base font-semibold text-white bg-indigo-600 hover:bg-indigo-500 shadow-xl shadow-indigo-600/25 transition-all flex items-center justify-center space-x-2"
              >
                <span>Get Started</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>

            {/* Interactive Agent Terminal Mockup */}
            <div className="mt-16 max-w-4xl mx-auto text-left rounded-2xl border border-slate-800 bg-slate-900/90 shadow-2xl shadow-black/80 overflow-hidden backdrop-blur-xl">
              <div className="bg-slate-950/80 px-4 py-3 border-b border-slate-800/80 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
                  <Terminal className="w-4 h-4 text-indigo-400" />
                  <span>
                    NetToHost Agent Workspace • target: prod-server-01
                  </span>
                </div>
                <div className="text-xs font-mono text-emerald-400 flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                  <span>2 HOSTS ONLINE</span>
                </div>
              </div>
              <div className="p-6 font-mono text-sm space-y-4">
                <div className="flex items-start space-x-3 text-slate-300">
                  <span className="text-indigo-400 font-bold">User:</span>
                  <span>
                    "Restart the Nginx service and verify system health on
                    prod-server-01"
                  </span>
                </div>
                <div className="flex items-start space-x-3 text-slate-400 bg-slate-950/60 p-3 rounded-lg border border-slate-800/60">
                  <span className="text-indigo-400 font-bold">Agent:</span>
                  <span>
                    Target host identified: <strong>prod-server-01</strong>.
                    Assessing action safety...
                  </span>
                </div>
                <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-950/20 text-amber-200 space-y-2">
                  <div className="flex items-center space-x-2 font-bold text-amber-400">
                    <ShieldAlert className="w-5 h-5" />
                    <span>
                      ⚠️ Safety Guardrail Interruption: Approval Required
                    </span>
                  </div>
                  <p className="text-xs text-amber-300/80">
                    Action: Restart service{" "}
                    <code className="bg-amber-900/40 px-1.5 py-0.5 rounded text-amber-200">
                      nginx.service
                    </code>{" "}
                    on host{" "}
                    <code className="bg-amber-900/40 px-1.5 py-0.5 rounded text-amber-200">
                      prod-server-01
                    </code>
                    .
                  </p>
                  <p className="text-xs text-amber-300/80">
                    Reason: Modifying system services requires explicit operator
                    confirmation.
                  </p>
                  <div className="flex space-x-3 pt-1">
                    <button className="px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 transition-colors shadow-sm">
                      Approve & Execute
                    </button>
                    <button className="px-3.5 py-1.5 rounded-lg bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700 transition-colors">
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Core Product Capabilities */}
        <section
          id="capabilities"
          className="py-20 border-t border-slate-800/60 bg-slate-950/50"
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl font-bold tracking-tight text-slate-100">
                Unified Remote Control & Tool Orchestration
              </h2>
              <p className="mt-4 text-slate-400 text-base">
                NetToHost connects your remote machines and host services into
                an intelligent conversational command center.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Feature 1 */}
              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 hover:border-slate-700 transition-all group">
                <div className="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/60 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
                  <Wrench className="w-6 h-6" />
                </div>
                <h3 className="mt-5 text-lg font-semibold text-slate-100">
                  Remote Tool Discovery
                </h3>
                <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                  Automatically sync and discover available tools, CLI
                  utilities, and MCP services running across connected host
                  devices.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 hover:border-slate-700 transition-all group">
                <div className="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/60 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
                  <ShieldAlert className="w-6 h-6" />
                </div>
                <h3 className="mt-5 text-lg font-semibold text-slate-100">
                  Human Approval Guardrails
                </h3>
                <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                  Automatic safety evaluation detects dangerous modifications
                  (deleting files, stopping services) and prompts for operator
                  confirmation before running.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 hover:border-slate-700 transition-all group">
                <div className="w-12 h-12 rounded-xl bg-indigo-950 border border-indigo-800/60 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
                  <Server className="w-6 h-6" />
                </div>
                <h3 className="mt-5 text-lg font-semibold text-slate-100">
                  Multi-Machine Workspaces
                </h3>
                <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                  Organize remote hosts into team workspaces. Generate secure
                  host authentication tokens and assign role permissions.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-8 text-slate-400 text-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <span className="font-semibold text-slate-200">
              NetToHost Platform
            </span>
            <span className="text-slate-500">•</span>
            <span className="flex items-center text-xs text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
              All Systems Operational
            </span>
          </div>
          <p className="text-xs text-slate-500">
            &copy; {new Date().getFullYear()} NetToHost. Autonomous Remote Tool
            Management.
          </p>
        </div>
      </footer>
    </div>
  )
}
