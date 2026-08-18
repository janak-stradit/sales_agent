// Mock Database for Enterprise Sales Chatbot Agent
const mockData = {
    // Current Active and Past Conversations
    conversations: [
        {
            id: "chat-001",
            leadName: "Sarah Jenkins",
            role: "Director of IT",
            company: "Apex Global Solutions",
            email: "sarah.jenkins@apexglobal.com",
            phone: "+1 (555) 234-5678",
            dealValue: 48000,
            status: "hot",
            intent: "pricing_inquiry",
            sentiment: "Positive (0.85)",
            confidence: 0.94,
            uptime: "Active Now",
            agentMode: "auto", // auto or manual (human-in-the-loop)
            messages: [
                {
                    sender: "user",
                    text: "Hi there, I'm the Director of IT at Apex Global. We're looking to scale our cloud infrastructure and want to know about your Enterprise pricing plans.",
                    time: "10:24 AM"
                },
                {
                    sender: "agent",
                    text: "Hello Sarah! Thanks for reaching out. I'd be happy to guide you through our enterprise cloud plans. For larger organizations like Apex Global, we offer tailored packages with custom SLAs, dedicated support, and volume discounts starting from $1,200/month. What is your estimated monthly transfer volume?",
                    time: "10:25 AM",
                    intelligence: {
                        intent: "pricing_inquiry",
                        sentiment: "Inquisitive",
                        confidence: 0.98,
                        retrievedKnowledge: "pricing_enterprise_slas, volume_discounts"
                    }
                },
                {
                    sender: "user",
                    text: "We currently process around 50TB of data per month but expect that to double by Q4. We also need strict HIPAA compliance.",
                    time: "10:26 AM"
                },
                {
                    sender: "agent",
                    text: "Understood. 50TB with HIPAA compliance fits perfectly within our secure Enterprise Tier. We guarantee 99.99% uptime, end-to-end data encryption, and we sign BAA agreements. For 50TB to 100TB, I can secure a custom pricing package of $2,400/month (a 20% volume discount). Would you like me to schedule a short demo with our cloud compliance architect?",
                    time: "10:27 AM",
                    intelligence: {
                        intent: "compliance_check",
                        sentiment: "Interested",
                        confidence: 0.95,
                        retrievedKnowledge: "hipaa_compliance_standard, baa_agreements, enterprise_pricing_tiers"
                    }
                }
            ],
            suggestedReplies: [
                {
                    tag: "Schedule Demo",
                    text: "I'd love to schedule that demo. Does Thursday at 2 PM EST work for you?",
                    action: "send_suggested"
                },
                {
                    tag: "Provide Brochure",
                    text: "Here is a link to our HIPAA Compliance Whitepaper and Enterprise datasheet.",
                    action: "send_suggested"
                },
                {
                    tag: "Discount Approval",
                    text: "Let me check with my sales director if we can do $2,200/month for a 2-year contract.",
                    action: "send_suggested"
                }
            ]
        },
        {
            id: "chat-002",
            leadName: "David Miller",
            role: "Product Manager",
            company: "Starlight Media",
            email: "d.miller@starlight.io",
            phone: "+1 (555) 987-6543",
            dealValue: 18500,
            status: "warm",
            intent: "product_comparison",
            sentiment: "Neutral (0.45)",
            confidence: 0.88,
            uptime: "2m ago",
            agentMode: "auto",
            messages: [
                {
                    sender: "user",
                    text: "How does your analytics engine compare to Mixpanel? We need real-time cohort tracking.",
                    time: "10:15 AM"
                },
                {
                    sender: "agent",
                    text: "Great question, David! Unlike Mixpanel which focuses primarily on product analytics, our engine unites product analytics with marketing attribution and sales CRM data. We support real-time cohort tracking with sub-second queries, and we don't charge extra for high event volume. Plus, you own your raw data.",
                    time: "10:16 AM",
                    intelligence: {
                        intent: "competitor_comparison",
                        sentiment: "Neutral",
                        confidence: 0.92,
                        retrievedKnowledge: "vs_mixpanel, raw_data_ownership, cohort_tracking"
                    }
                },
                {
                    sender: "user",
                    text: "That sounds promising. Do you have a self-serve trial for this, or do we have to talk to sales?",
                    time: "10:18 AM"
                }
            ],
            suggestedReplies: [
                {
                    tag: "Free Trial Link",
                    text: "Yes, you can sign up for a 14-day free trial right now at our website. No credit card required!",
                    action: "send_suggested"
                },
                {
                    tag: "Interactive Tour",
                    text: "You can try our interactive sandbox environment here to see how cohorts are configured.",
                    action: "send_suggested"
                }
            ]
        },
        {
            id: "chat-003",
            leadName: "Elena Rostova",
            role: "VP of Security",
            company: "FinTech Innovations",
            email: "elena@fintechin.de",
            phone: "+49 89 1234567",
            dealValue: 85000,
            status: "hot",
            intent: "security_compliance",
            sentiment: "Positive (0.78)",
            confidence: 0.97,
            uptime: "15m ago",
            agentMode: "manual", // Human-in-the-loop takeover active
            messages: [
                {
                    sender: "user",
                    text: "We require SOC2 Type II certification and on-premise deployment options. Is that supported?",
                    time: "09:45 AM"
                },
                {
                    sender: "agent",
                    text: "Yes, Elena. We hold a SOC2 Type II certification (audited annually) and support hybrid/on-premise deployment via Kubernetes (EKS, GKE, or self-managed). I've marked this conversation for human assistance so our Enterprise Architect can join.",
                    time: "09:47 AM",
                    intelligence: {
                        intent: "soc2_compliance, on_prem_deployment",
                        sentiment: "Serious",
                        confidence: 0.99,
                        retrievedKnowledge: "soc2_cert, hybrid_kubernetes_deployments"
                    }
                },
                {
                    sender: "user",
                    text: "Excellent. Can we receive your latest SOC2 compliance report under NDA?",
                    time: "09:50 AM"
                }
            ],
            suggestedReplies: [
                {
                    tag: "Send NDA Link",
                    text: "I am sending you the link to our digital NDA. Once signed, the SOC2 report will download automatically.",
                    action: "send_suggested"
                },
                {
                    tag: "Architect Call",
                    text: "I've added our architect to this chat thread. Let's find a time for a deeper technical review.",
                    action: "send_suggested"
                }
            ]
        },
        {
            id: "chat-004",
            leadName: "Marcus Thorne",
            role: "Operations Team Lead",
            company: "Thorne Logistics",
            email: "marcus@thornelogistics.com",
            phone: "+1 (555) 432-1098",
            dealValue: 12000,
            status: "cold",
            intent: "support_issue",
            sentiment: "Negative (-0.60)",
            confidence: 0.81,
            uptime: "1h ago",
            agentMode: "auto",
            messages: [
                {
                    sender: "user",
                    text: "Your integration is dropping webhook payloads. We've lost track of 15 orders today.",
                    time: "08:12 AM"
                },
                {
                    sender: "agent",
                    text: "I am very sorry to hear that, Marcus. This sounds like a critical webhook retry issue. I'm checking our status page and our integration logs right now. Could you confirm which endpoint URL is experiencing the drops?",
                    time: "08:14 AM",
                    intelligence: {
                        intent: "webhook_bug_report",
                        sentiment: "Frustrated",
                        confidence: 0.89,
                        retrievedKnowledge: "webhook_retry_policy, status_page_check"
                    }
                }
            ],
            suggestedReplies: [
                {
                    tag: "Escalate to Support",
                    text: "I have escalated this ticket to our Tier 3 engineering support. They will contact you within 15 minutes.",
                    action: "send_suggested"
                },
                {
                    tag: "Check Retries",
                    text: "Please try changing your endpoint timeout limit to 5000ms. I will queue a replay of all failed events.",
                    action: "send_suggested"
                }
            ]
        }
    ],

    // Captured Leads Database
    leads: [
        { id: "L-101", name: "Sarah Jenkins", role: "Director of IT", company: "Apex Global Solutions", email: "sarah.jenkins@apexglobal.com", dealValue: 48000, status: "Hot", source: "Website Chatbot", lastActive: "Just Now" },
        { id: "L-102", name: "David Miller", role: "Product Manager", company: "Starlight Media", email: "d.miller@starlight.io", dealValue: 18500, status: "Warm", source: "Pricing Page Bot", lastActive: "2 min ago" },
        { id: "L-103", name: "Elena Rostova", role: "VP of Security", company: "FinTech Innovations", email: "elena@fintechin.de", dealValue: 85000, status: "Hot", source: "LinkedIn Inbound", lastActive: "15 min ago" },
        { id: "L-104", name: "Marcus Thorne", role: "Operations Team Lead", company: "Thorne Logistics", email: "marcus@thornelogistics.com", dealValue: 12000, status: "Cold", source: "Docs Chatbot", lastActive: "1 hour ago" },
        { id: "L-105", name: "Hiroshi Tanaka", role: "CEO", company: "Tokyo Automations", email: "h.tanaka@tokyoauto.jp", dealValue: 150000, status: "Hot", source: "Partner Referral", lastActive: "1 day ago" },
        { id: "L-106", name: "Sophia Martinez", role: "Chief Medical Officer", company: "BrightCare Health", email: "smartinez@brightcare.org", dealValue: 32000, status: "Warm", source: "HIPAA Demo Request", lastActive: "3 days ago" }
    ],

    // Default Configuration for the AI Agent
    agentConfig: {
        agentName: "Anna",
        role: "Enterprise Sales Specialist",
        temperature: 0.2,
        systemPrompt: "You are Anna, an elite enterprise sales specialist for SaaS platforms. Your goal is to qualify leads, capture company requirements (budget, volume, compliance, timelines), provide precise product positioning against competitors, handle pricing objections, and book high-quality meetings for the executive sales team. Always maintain a professional, helpful, and solution-oriented tone. Highlight our SOC2 compliance, 99.99% uptime SLA, and custom enterprise deployments.",
        model: "gpt-4o-enterprise",
        leadCaptureFields: ["Company Name", "Monthly Volume", "Compliance Standard", "Email/Phone", "Project Timeline"],
        faqs: [
            { question: "What is your pricing?", answer: "Enterprise packages starting at $1,200/month with custom volume discounting available." },
            { question: "Are you compliance certified?", answer: "Yes, we are fully SOC2 Type II, HIPAA, and GDPR compliant." },
            { question: "Do you offer proof of concepts?", answer: "We provide 14-day fully-featured sandbox environments and guided 30-day POC programs." }
        ]
    },

    // Daily and Cumulative Metrics
    metrics: {
        todayConversations: 142,
        activeChats: 4,
        conversionRate: 24.8,
        conversionTrend: "+3.2%",
        pipelineGenerated: 345500,
        pipelineTrend: "+18.5%",
        aiDeflectionRate: 88.5,
        aiDeflectionTrend: "+0.8%",
        csatScore: 4.85,
        csatTrend: "+2.1%"
    },

    // Chart Data Over Time
    analyticsData: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        conversations: [120, 145, 160, 138, 172, 95, 80],
        leadsCaptured: [18, 28, 35, 24, 42, 10, 8],
        revenueGenerated: [45000, 68000, 92000, 52000, 115000, 25000, 18000],
        intentDistribution: {
            labels: ["Pricing Inquiry", "Security & Compliance", "Product Comparison", "Support Escalation", "Integration Specs"],
            data: [40, 20, 22, 10, 8]
        }
    }
};
