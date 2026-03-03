'use client';
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Menu, X, Github, Info, Upload } from 'lucide-react';

interface NavigationProps {
  className?: string;
}

const Navigation: React.FC<NavigationProps> = ({ className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => setIsOpen(!isOpen);

  const navItems = [
    { name: 'Analyze', href: '#upload', icon: Upload },
    { name: 'About', href: '#about', icon: Info },
    { name: 'GitHub', href: '#github', icon: Github },
  ];

  return (
    <motion.nav
      className={`fixed top-0 left-0 right-0 z-50 ${className}`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="glass-morphism-dark border-b border-gray-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <motion.div 
              className="flex items-center space-x-3"
              whileHover={{ scale: 1.05 }}
            >
              <div className="relative">
                <Shield className="w-8 h-8 text-blue-400" />
                <motion.div
                  className="absolute -inset-1 bg-blue-400/20 rounded-full blur-sm"
                  animate={{ 
                    scale: [1, 1.2, 1],
                    opacity: [0.3, 0.6, 0.3]
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                  DeepGuard
                </h1>
                <p className="text-xs text-gray-400 -mt-1">AI Detection</p>
              </div>
            </motion.div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              {navItems.map((item, index) => (
                <motion.a
                  key={item.name}
                  href={item.href}
                  className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors duration-200"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <item.icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </motion.a>
              ))}
              
              {/* Status Indicator */}
              <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-green-900/30 border border-green-500/30">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-green-300 text-sm">Online</span>
              </div>
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden">
              <motion.button
                onClick={toggleMenu}
                className="text-gray-300 hover:text-white p-2"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </motion.button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <motion.div
          className={`md:hidden overflow-hidden border-t border-gray-700/50 ${
            isOpen ? 'max-h-64' : 'max-h-0'
          }`}
          animate={{ 
            maxHeight: isOpen ? 256 : 0,
            opacity: isOpen ? 1 : 0
          }}
          transition={{ duration: 0.3 }}
        >
          <div className="px-4 py-4 space-y-4">
            {navItems.map((item, index) => (
              <motion.a
                key={item.name}
                href={item.href}
                className="flex items-center space-x-3 text-gray-300 hover:text-white transition-colors duration-200 py-2"
                onClick={() => setIsOpen(false)}
                initial={{ opacity: 0, x: -20 }}
                animate={{ 
                  opacity: isOpen ? 1 : 0,
                  x: isOpen ? 0 : -20
                }}
                transition={{ delay: index * 0.1 }}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.name}</span>
              </motion.a>
            ))}
            
            <div className="flex items-center space-x-3 py-2 border-t border-gray-700/50 mt-4 pt-4">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-green-300 text-sm">System Online</span>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.nav>
  );
};

export default Navigation;