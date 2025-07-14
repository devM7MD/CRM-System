<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRM System - README</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    animation: {
                        'fade-in': 'fadeIn 0.5s ease-in',
                        'slide-up': 'slideUp 0.6s ease-out',
                        'bounce-subtle': 'bounceSubtle 2s infinite',
                    },
                    keyframes: {
                        fadeIn: {
                            '0%': { opacity: '0' },
                            '100%': { opacity: '1' }
                        },
                        slideUp: {
                            '0%': { transform: 'translateY(20px)', opacity: '0' },
                            '100%': { transform: 'translateY(0)', opacity: '1' }
                        },
                        bounceSubtle: {
                            '0%, 100%': { transform: 'translateY(0)' },
                            '50%': { transform: 'translateY(-5px)' }
                        }
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 min-h-screen text-white">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <!-- Header -->
        <header class="text-center mb-12 animate-fade-in">
            <div class="relative">
                <h1 class="text-6xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-4 animate-bounce-subtle">
                    CRM-SYSTEM
                </h1>
                <div class="absolute inset-0 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 blur-3xl opacity-20 -z-10"></div>
            </div>
            <p class="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
                A modern, scalable Customer Relationship Management system built with cutting-edge technologies
            </p>
            <div class="flex justify-center space-x-4 mt-6">
                <span class="px-4 py-2 bg-green-600 rounded-full text-sm font-semibold">v2.1.0</span>
                <span class="px-4 py-2 bg-blue-600 rounded-full text-sm font-semibold">Production Ready</span>
                <span class="px-4 py-2 bg-purple-600 rounded-full text-sm font-semibold">MIT License</span>
            </div>
        </header>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 animate-slide-up">
            <div class="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 group">
                <div class="text-3xl mb-3 group-hover:scale-110 transition-transform">🚀</div>
                <h3 class="text-xl font-semibold mb-2">Quick Start</h3>
                <p class="text-gray-300 text-sm">Get up and running in minutes with our streamlined setup process</p>
            </div>
            <div class="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 group">
                <div class="text-3xl mb-3 group-hover:scale-110 transition-transform">📚</div>
                <h3 class="text-xl font-semibold mb-2">Documentation</h3>
                <p class="text-gray-300 text-sm">Comprehensive guides and API references for developers</p>
            </div>
            <div class="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-300 group">
                <div class="text-3xl mb-3 group-hover:scale-110 transition-transform">🔧</div>
                <h3 class="text-xl font-semibold mb-2">Configuration</h3>
                <p class="text-gray-300 text-sm">Flexible settings to customize your CRM experience</p>
            </div>
        </div>

        <!-- Features Section -->
        <section class="mb-12 animate-slide-up">
            <h2 class="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                ✨ Features
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-4">
                    <div class="flex items-center space-x-3 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                        <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                        <span class="text-lg">Customer Management & 360° View</span>
                    </div>
                    <div class="flex items-center space-x-3 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                        <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
                        <span class="text-lg">Sales Pipeline & Opportunity Tracking</span>
                    </div>
                    <div class="flex items-center space-x-3 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                        <div class="w-2 h-2 bg-purple-400 rounded-full"></div>
                        <span class="text-lg">Advanced Analytics & Reporting</span>
                    </div>
                    <div class="flex items-center space-x-3 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                        <div class="w-2 h-2 bg-pink-400 rounded-full"></div>
                        <span class="text-lg">Task & Activity Management</span>
                    </div>
                </div>
                <div class="space-y-4">
                    <div class="flex items-center space-x-3 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                        <div class="w-2 h-2 bg-yellow-400 rounded-full"></div>
                        <span class="text-lg">Email Integration & Automation</span>
                    </div>
                    <div class="flex items-center space-x-3 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                        <div class="w-2 h-2 bg-red-400 rounded-full"></div>
                        <span class="text-lg">Role-Based Access Control</span>
                    </div>
                    <div class="flex items-center space-x-3 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                        <div class="w-2 h-2 bg-indigo-400 rounded-full"></div>
                        <span class="text-lg">Mobile-First Responsive Design</span>
                    </div>
                    <div class="flex items-center space-x-3 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                        <div class="w-2 h-2 bg-teal-400 rounded-full"></div>
                        <span class="text-lg">Third-Party Integrations</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- Tech Stack -->
        <section class="mb-12 animate-slide-up">
            <h2 class="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
                🛠️ Tech Stack
            </h2>
            <div class="bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-white/20">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div>
                        <h3 class="text-xl font-semibold mb-4 text-cyan-400">Frontend</h3>
                        <ul class="space-y-2 text-gray-300">
                            <li>• React 18 with TypeScript</li>
                            <li>• Redux Toolkit for state management</li>
                            <li>• Material-UI & Tailwind CSS</li>
                            <li>• Chart.js for data visualization</li>
                        </ul>
                    </div>
                    <div>
                        <h3 class="text-xl font-semibold mb-4 text-green-400">Backend</h3>
                        <ul class="space-y-2 text-gray-300">
                            <li>• Node.js with Express.js</li>
                            <li>• PostgreSQL database</li>
                            <li>• Redis for caching</li>
                            <li>• JWT authentication</li>
                        </ul>
                    </div>
                    <div>
                        <h3 class="text-xl font-semibold mb-4 text-purple-400">DevOps</h3>
                        <ul class="space-y-2 text-gray-300">
                            <li>• Docker containerization</li>
                            <li>• GitHub Actions CI/CD</li>
                            <li>• AWS deployment</li>
                            <li>• Monitoring with Prometheus</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <!-- Installation -->
        <section class="mb-12 animate-slide-up">
            <h2 class="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                🚀 Installation
            </h2>
            <div class="space-y-6">
                <div class="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-700">
                    <h3 class="text-xl font-semibold mb-4 text-green-400">Prerequisites</h3>
                    <ul class="space-y-2 text-gray-300">
                        <li>• Node.js 18+ and npm/yarn</li>
                        <li>• PostgreSQL 14+</li>
                        <li>• Redis 6+</li>
                        <li>• Git</li>
                    </ul>
                </div>
                
                <div class="bg-gray-900/50 backdrop-blur-lg rounded-xl p-6 border border-gray-700">
                    <h3 class="text-xl font-semibold mb-4 text-blue-400">Quick Setup</h3>
                    <div class="bg-black/50 rounded-lg p-4 font-mono text-sm">
                        <div class="text-gray-400 mb-2"># Clone the repository</div>
                        <div class="text-green-400">git clone https://github.com/yourorg/crm-system.git</div>
                        <div class="text-green-400">cd crm-system</div>
                        <br>
                        <div class="text-gray-400 mb-2"># Install dependencies</div>
                        <div class="text-green-400">npm install</div>
                        <br>
                        <div class="text-gray-400 mb-2"># Setup environment</div>
                        <div class="text-green-400">cp .env.example .env</div>
                        <div class="text-green-400">npm run setup</div>
                        <br>
                        <div class="text-gray-400 mb-2"># Start development server</div>
                        <div class="text-green-400">npm run dev</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Usage -->
        <section class="mb-12 animate-slide-up">
            <h2 class="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-pink-400 to-red-400 bg-clip-text text-transparent">
                💡 Usage
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                    <h3 class="text-xl font-semibold mb-4 text-cyan-400">Development</h3>
                    <div class="bg-black/30 rounded-lg p-4 font-mono text-sm">
                        <div class="text-green-400">npm run dev</div>
                        <div class="text-gray-400 text-xs mt-2">Starts the development server at http://localhost:3000</div>
                    </div>
                </div>
                <div class="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                    <h3 class="text-xl font-semibold mb-4 text-green-400">Production</h3>
                    <div class="bg-black/30 rounded-lg p-4 font-mono text-sm">
                        <div class="text-green-400">npm run build</div>
                        <div class="text-green-400">npm start</div>
                        <div class="text-gray-400 text-xs mt-2">Builds and runs the production server</div>
                    </div>
                </div>
                <div class="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                    <h3 class="text-xl font-semibold mb-4 text-purple-400">Testing</h3>
                    <div class="bg-black/30 rounded-lg p-4 font-mono text-sm">
                        <div class="text-green-400">npm run test</div>
                        <div class="text-green-400">npm run test:coverage</div>
                        <div class="text-gray-400 text-xs mt-2">Run tests with coverage report</div>
                    </div>
                </div>
                <div class="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                    <h3 class="text-xl font-semibold mb-4 text-yellow-400">Docker</h3>
                    <div class="bg-black/30 rounded-lg p-4 font-mono text-sm">
                        <div class="text-green-400">docker-compose up -d</div>
                        <div class="text-gray-400 text-xs mt-2">Start with Docker Compose</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Configuration -->
        <section class="mb-12 animate-slide-up">
            <h2 class="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                ⚙️ Configuration
            </h2>
            <div class="bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-white/20">
                <h3 class="text-xl font-semibold mb-4 text-green-400">Environment Variables</h3>
                <div class="bg-black/50 rounded-lg p-4 font-mono text-sm overflow-x-auto">
                    <div class="text-gray-400"># Database Configuration</div>
                    <div class="text-blue-400">DATABASE_URL=postgresql://user:password@localhost:5432/crm_db</div>
                    <div class="text-blue-400">REDIS_URL=redis://localhost:6379</div>
                    <br>
                    <div class="text-gray-400"># Authentication</div>
                    <div class="text-blue-400">JWT_SECRET=your-super-secret-jwt-key</div>
                    <div class="text-blue-400">JWT_EXPIRES_IN=24h</div>
                    <br>
                    <div class="text-gray-400"># Email Service</div>
                    <div class="text-blue-400">SMTP_HOST=smtp.gmail.com</div>
                    <div class="text-blue-400">SMTP_PORT=587</div>
                    <div class="text-blue-400">SMTP_USER=your-email@gmail.com</div>
                    <div class="text-blue-400">SMTP_PASS=your-app-password</div>
                    <br>
                    <div class="text-gray-400"># Application Settings</div>
                    <div class="text-blue-400">PORT=3000</div>
                    <div class="text-blue-400">NODE_ENV=development</div>
                </div>
            </div>
        </section>

        <!-- API Documentation -->
        <section class="mb-12 animate-slide-up">
            <h2 class="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-teal-400 to-green-400 bg-clip-text text-transparent">
                📡 API Documentation
            </h2>
            <div class="space-y-6">
                <div class="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                    <h3 class="text-xl font-semibold mb-4 text-blue-400">Authentication Endpoints</h3>
                    <div class="space-y-2 text-sm">
                        <div class="flex items-center space-x-4">
                            <span class="px-2 py-1 bg-green-600 rounded text-xs">POST</span>
                            <span class="font-mono text-gray-300">/api/auth/login</span>
                            <span class="text-gray-400">- User login</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <span class="px-2 py-1 bg-blue-600 rounded text-xs">POST</span>
                            <span class="font-mono text-gray-300">/api/auth/register</span>
                            <span class="text-gray-400">- User registration</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <span class="px-2 py-1 bg-red-600 rounded text-xs">POST</span>
                            <span class="font-mono text-gray-300">/api/auth/logout</span>
                            <span class="text-gray-400">- User logout</span>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                    <h3 class="text-xl font-semibold mb-4 text-purple-400">Customer Management</h3>
                    <div class="space-y-2 text-sm">
                        <div class="flex items-center space-x-4">
                            <span class="px-2 py-1 bg-green-600 rounded text-xs">GET</span>
                            <span class="font-mono text-gray-300">/api/customers</span>
                            <span class="text-gray-400">- Get all customers</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <span class="px-2 py-1 bg-blue-600 rounded text-xs">POST</span>
                            <span class="font-mono text-gray-300">/api/customers</span>
                            <span class="text-gray-400">- Create new customer</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <span class="px-2 py-1 bg-yellow-600 rounded text-xs">PUT</span>
                            <span class="font-mono text-gray-300">/api/customers/:id</span>
                            <span class="text-gray-400">- Update customer</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Contributing -->
        <section class="mb-12 animate-slide-up">
            <h2 class="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">
                🤝 Contributing
            </h2>
            <div class="bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-white/20">
                <p class="text-lg text-gray-300 mb-6">
                    We welcome contributions! Please see our contributing guidelines and code of conduct.
                </p>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h3 class="text-xl font-semibold mb-4 text-green-400">Development Process</h3>
                        <ol class="space-y-2 text-gray-300">
                            <li>1. Fork the repository</li>
                            <li>2. Create a feature branch</li>
                            <li>3. Make your changes</li>
                            <li>4. Write tests</li>
                            <li>5. Submit a pull request</li>
                        </ol>
                    </div>
                    <div>
                        <h3 class="text-xl font-semibold mb-4 text-blue-400">Code Standards</h3>
                        <ul class="space-y-2 text-gray-300">
                            <li>• Follow ESLint configuration</li>
                            <li>• Write comprehensive tests</li>
                            <li>• Document new features</li>
                            <li>• Use TypeScript strictly</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <!-- Footer -->
        <footer class="text-center pt-8 border-t border-white/20 animate-fade-in">
            <div class="flex justify-center space-x-8 mb-6">
                <a href="#" class="text-gray-400 hover:text-white transition-colors">📧 Support</a>
                <a href="#" class="text-gray-400 hover:text-white transition-colors">📖 Documentation</a>
                <a href="#" class="text-gray-400 hover:text-white transition-colors">🐛 Issues</a>
                <a href="#" class="text-gray-400 hover:text-white transition-colors">🌟 GitHub</a>
            </div>
            <p class="text-gray-400 text-sm">
                Built with ❤️ by the CRM Team | Licensed under MIT
            </p>
        </footer>
    </div>
</body>
</html>
