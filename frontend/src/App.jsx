import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Send, Scale, ChevronDown, ChevronUp, Bot, User, Loader2 } from 'lucide-react';

const API_URL = "http://localhost:8000/api/chat";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(API_URL, { query: input });
      const data = response.data;
      
      const assistantMessage = {
        role: 'assistant',
        raw: data
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error fetching response:", error);
      const errorMessage = {
        role: 'assistant',
        content: "Sorry, I encountered an error connecting to the server. Please make sure the backend is running."
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100 font-sans selection:bg-indigo-500/30">
      {/* Sidebar */}
      <div className="hidden md:flex w-64 flex-col bg-gray-800 border-r border-gray-700">
        <div className="p-6 flex items-center gap-3 border-b border-gray-700">
          <div className="p-2 bg-indigo-500 rounded-lg">
            <Scale size={24} className="text-white" />
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            LegalEase
          </h1>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          <p className="text-sm text-gray-400 mb-4">Your elite Trial Advocate and RAG-powered Legal Assistant.</p>
          <div className="space-y-2">
             {/* Future session history could go here */}
          </div>
        </div>
        <div className="p-4 border-t border-gray-700 text-xs text-gray-500 text-center">
          Powered by gpt-oss:120b
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative">
        {/* Header (Mobile) */}
        <div className="md:hidden flex items-center p-4 bg-gray-800 border-b border-gray-700">
          <Scale size={20} className="text-indigo-400 mr-2" />
          <h1 className="font-bold">LegalEase</h1>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-4 opacity-70">
              <Scale size={64} className="text-gray-600" />
              <h2 className="text-2xl font-bold text-gray-400">How can I assist you today?</h2>
              <p className="text-gray-500 max-w-md">Ask a legal question, and I will analyze the statutes to formulate a strategic response.</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <ChatMessage key={index} message={msg} />
            ))
          )}
          {isLoading && (
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center border border-indigo-500/50 flex-shrink-0">
                <Loader2 size={16} className="text-indigo-400 animate-spin" />
              </div>
              <div className="bg-gray-800 border border-gray-700 rounded-2xl p-4 shadow-sm">
                <p className="text-gray-400 text-sm animate-pulse">Analyzing legal statutes...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-gray-900 border-t border-gray-800">
          <div className="max-w-4xl mx-auto relative">
            <form onSubmit={handleSubmit} className="relative flex items-center">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a legal question..."
                className="w-full bg-gray-800 border border-gray-700 text-gray-100 rounded-full pl-6 pr-14 py-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-lg transition-all"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="absolute right-2 p-2.5 bg-indigo-500 hover:bg-indigo-600 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-full transition-colors"
              >
                <Send size={18} />
              </button>
            </form>
            <p className="text-xs text-center text-gray-500 mt-3">LegalEase can make mistakes. Verify important information.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} gap-2 w-full`}>
      <div className={`flex items-start gap-3 max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 ${
          isUser ? 'bg-gray-700 text-gray-300' : 'bg-indigo-500/20 border border-indigo-500/50 text-indigo-400'
        }`}>
          {isUser ? <User size={16} /> : <Scale size={16} />}
        </div>

        {/* Message Bubble */}
        <div className={`rounded-2xl px-5 py-4 shadow-sm ${
          isUser 
            ? 'bg-gray-800 border border-gray-700 text-gray-200' 
            : 'bg-transparent w-full'
        }`}>
          {isUser ? (
             <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <AssistantResponse raw={message.raw} fallbackContent={message.content} />
          )}
        </div>
      </div>
    </div>
  );
}

function AssistantResponse({ raw, fallbackContent }) {
  if (fallbackContent) {
    return <p className="text-red-400">{fallbackContent}</p>;
  }

  if (!raw) return null;

  let answer = raw.answer || raw.answer_text || "No answer found.";

  // Quick fallback cleanup if backend sent a raw JSON string instead of parsed JSON
  if (typeof answer === 'string' && answer.trim().startsWith('{') && answer.includes('"answer"')) {
    try {
      const parsed = JSON.parse(answer);
      if (parsed.answer) answer = parsed.answer;
    } catch (e) {
      const match = answer.match(/"answer"\s*:\s*"([\s\S]*?)"\s*(?:,"|\})/);
      if (match) {
        answer = match[1].replace(/\\n/g, '\n').replace(/\\"/g, '"');
      }
    }
  }

  const legalTerms = raw.legal_terms || [];
  const relevantArticles = raw.relevant_articles || [];
  const confidence = raw.confidence || (raw.answer_text ? "high" : "Unknown");

  return (
    <div className="space-y-6 w-full text-gray-200 leading-relaxed">
      {/* Markdown Answer */}
      <div className="prose prose-invert max-w-none">
        <ReactMarkdown>{answer}</ReactMarkdown>
      </div>

      {/* Legal Terms Cards */}
      {legalTerms.length > 0 && (
        <div className="mt-8 border-t border-gray-800 pt-6">
          <h4 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <Bot size={16} /> Legal Terms & Citations
          </h4>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {legalTerms.map((term, i) => (
              <div key={i} className="bg-gray-800/50 border border-gray-700 rounded-xl p-4 hover:border-indigo-500/50 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <h5 className="font-semibold text-indigo-300">{term.term || 'N/A'}</h5>
                  <span className="text-xs px-2 py-1 bg-gray-700 rounded text-gray-300">{term.source || 'Context'}</span>
                </div>
                <p className="text-sm text-gray-400 mb-2">Citation: {term.article || 'N/A'}</p>
                <div className="bg-gray-900/50 p-3 rounded-lg border border-gray-800">
                  <p className="text-xs italic text-gray-500">"{term.quote}"</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Relevant Articles */}
      {relevantArticles.length > 0 && (
        <div className="mt-4">
          <ExpandableSection title="View Referenced Articles">
            <div className="space-y-3 pt-2">
              {relevantArticles.map((art, i) => (
                <div key={i} className="pl-4 border-l-2 border-indigo-500/30">
                  <strong className="block text-indigo-400 text-sm mb-1">{art.article}</strong>
                  <p className="text-sm text-gray-400">{art.reason}</p>
                </div>
              ))}
            </div>
          </ExpandableSection>
        </div>
      )}

    </div>
  );
}

function ExpandableSection({ title, children }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border border-gray-700 rounded-xl overflow-hidden bg-gray-800/30">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-800/50 transition-colors"
      >
        <span className="text-sm font-semibold text-gray-300">{title}</span>
        {isOpen ? <ChevronUp size={16} className="text-gray-500" /> : <ChevronDown size={16} className="text-gray-500" />}
      </button>
      {isOpen && (
        <div className="p-4 border-t border-gray-700 bg-gray-900/20">
          {children}
        </div>
      )}
    </div>
  );
}
