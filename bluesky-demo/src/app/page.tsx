"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useState, useEffect } from "react"
import { Copy, Check } from "lucide-react"

export default function Home() {
  const [token, setToken] = useState("")
  const [copied, setCopied] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const response = await fetch('/api/token')
        const data = await response.json()
        
        if (data.error) {
          setError(data.error)
        } else {
          setToken(data.token)
        }
      } catch (err) {
        setError('Failed to fetch token: ' + err)
      }
    }

    fetchToken()
  }, [])

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(token)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <main className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <div className="max-w-2xl w-full space-y-6 text-center">
        <h1 className="text-4xl font-bold tracking-tight">Bluesky chat demo</h1>
        <p className="text-muted-foreground">This page is part of the mcp-tinybird Bluesky demo. Get your token below, and use with Claude Desktop to chat with Bluesky.</p>
        
        {error ? (
          <p className="text-destructive">{error}</p>
        ) : (
          <div className="flex w-full max-w-sm space-x-2 mx-auto">
            <Input
              type="text"
              value={token}
              readOnly
            />
            <Button
              variant="outline"
              size="icon"
              onClick={copyToClipboard}
              disabled={!token}
            >
              {copied ? (
                <Check className="h-4 w-4" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>
        )}
      </div>
    </main>
  )
}
