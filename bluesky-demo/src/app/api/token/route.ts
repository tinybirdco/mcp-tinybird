import { SignJWT } from 'jose'
import { NextResponse } from 'next/server'

export async function GET() {
    const signingKey = process.env.TINYBIRD_SIGNING_KEY
    const pipes = process.env.TINYBIRD_PIPES

    if (!signingKey) {
        return NextResponse.json(
            { error: 'TINYBIRD_SIGNING_KEY environment variable is not set' },
            { status: 500 }
        )
    }

    try {
        const encoder = new TextEncoder()
        const secretKey = encoder.encode(signingKey)

        // Generate scopes from pipes list
        const scopes = pipes 
            ? pipes.split(',').map(pipe => ({
                type: 'PIPES:READ',
                resource: pipe.trim()
            }))
            : []

        const jwt = await new SignJWT({
            workspace_id: process.env.TINYBIRD_WORKSPACE_ID,
            name: 'Tinybird Demo',
            scopes,
            limits: { rps: 1 }
        })
            .setProtectedHeader({ alg: 'HS256' })
            .setIssuedAt()
            .setExpirationTime('1d')
            .sign(secretKey)

        return NextResponse.json({ token: jwt })
    } catch (error) {
        console.error('Error generating token:', error)
        return NextResponse.json(
            { error: 'Failed to generate token' },
            { status: 500 }
        )
    }
}