'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import React from 'react'
import Icon from '@/components/ui/icon/Icon'
import { IconType } from '@/components/ui/icon/types'

const EXTERNAL_LINKS = {
    repo: 'https://github.com/Ash-Blanc/paper2saas',
    agenOS: 'https://os.agno.com'
}

interface ActionButtonProps {
    href: string
    variant?: 'primary'
    text: string
    icon?: IconType  // Use IconType instead of string
}

const ActionButton = ({ href, variant, text, icon }: ActionButtonProps) => {
    const baseStyles =
        'px-5 py-2.5 text-sm transition-colors font-dmmono tracking-tight flex items-center gap-2.5'  // Added flex + gap

    const variantStyles = {
        primary: 'border border-border hover:bg-neutral-800 rounded-xl'
    }

    return (
        <Link
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className={`${baseStyles} ${variant ? variantStyles[variant] : ''}`}
        >
            {text}
            {icon && <Icon type={icon} size="xs" />}
        </Link>
    )
}

const ChatBlankState = () => {
    return (
        <section
            className="flex flex-col items-center text-center font-geist"
            aria-label="Welcome message"
        >
            <div className="flex max-w-3xl flex-col gap-y-8">

                <motion.h1
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                    className="text-3xl font-[600] tracking-tight"
                >
                    <div className="text-5xl flex items-center justify-center gap-4">
                        <Icon
                            type="p2s"
                            className="w-7 h-7 md:w-10 md:h-10"
                        />
                        <span className="text-[#a09794]">P2S</span>
                    </div>
                    Multi-agent system for analyzing arXiv papers and generating SaaS ideas
                </motion.h1>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.5 }}
                    className="flex justify-center gap-6 flex-wrap"  // Added flex-wrap for mobile
                >
                    <ActionButton
                        href={EXTERNAL_LINKS.repo}
                        variant="primary"
                        text="STAR US"
                        icon='github'  // Assuming you have a 'github' icon in your Icon component
                    />
                </motion.div>
            </div>
        </section>
    )
}

export default ChatBlankState