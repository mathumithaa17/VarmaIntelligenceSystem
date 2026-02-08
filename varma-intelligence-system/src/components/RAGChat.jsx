import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader, AlertCircle } from 'lucide-react';
import varmaService from '../services/varmaService';

const RAGChat = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your Varma knowledge assistant. Ask me anything about Varma points, their locations, applications, or traditional medical knowledge.',
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Function to render markdown-formatted content
  const renderMarkdownContent = (content) => {
    const lines = content.split('\n');
    const elements = [];

    lines.forEach((line, lineIdx) => {
      if (!line.trim()) {
        elements.push(<div key={`space-${lineIdx}`} className="h-2" />);
        return;
      }

      // Handle numbered lists (1. , 2. , etc.)
      const numberedMatch = line.match(/^(\d+)\.\s+(.+)$/);
      if (numberedMatch) {
        elements.push(
          <div key={`numbered-${lineIdx}`} className="ml-4 my-2">
            <p className="text-sm leading-relaxed">
              <span className="font-semibold">{numberedMatch[1]}.</span> {renderInlineMarkdown(numberedMatch[2])}
            </p>
          </div>
        );
        return;
      }

      // Handle bullet points (-, •, *)
      const bulletMatch = line.match(/^[-•*]\s+(.+)$/);
      if (bulletMatch) {
        elements.push(
          <div key={`bullet-${lineIdx}`} className="ml-4 my-1">
            <p className="text-sm leading-relaxed">
              <span className="mr-2">•</span>{renderInlineMarkdown(bulletMatch[1])}
            </p>
          </div>
        );
        return;
      }

      // Handle headers (# , ## , etc.)
      const headerMatch = line.match(/^(#{1,6})\s+(.+)$/);
      if (headerMatch) {
        const level = headerMatch[1].length;
        const headerClasses = {
          1: 'text-lg font-bold mt-3 mb-2 text-gray-900',
          2: 'text-base font-bold mt-2 mb-2 text-gray-900',
          3: 'text-sm font-semibold mt-2 mb-1 text-gray-800',
          4: 'text-sm font-semibold text-gray-800',
          5: 'text-sm font-medium text-gray-800',
          6: 'text-sm font-medium text-gray-700',
        };
        
        elements.push(
          <p key={`header-${lineIdx}`} className={headerClasses[level]}>
            {renderInlineMarkdown(headerMatch[2])}
          </p>
        );
        return;
      }

      // Regular paragraph with inline markdown
      elements.push(
        <p key={`p-${lineIdx}`} className="text-sm leading-relaxed">
          {renderInlineMarkdown(line)}
        </p>
      );
    });

    return <div className="space-y-2">{elements}</div>;
  };

  // Function to handle inline markdown formatting
  const renderInlineMarkdown = (text) => {
    const parts = [];
    let remaining = text;

    // Pattern: **bold** and *italic*
    const combinedRegex = /\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`/g;
    let match;
    let lastIndex = 0;

    while ((match = combinedRegex.exec(text)) !== null) {
      // Add text before match
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }

      // Check which pattern matched
      if (match[1]) {
        // **bold** text
        parts.push(
          <strong key={`bold-${match.index}`} className="font-semibold text-gray-900">
            {match[1]}
          </strong>
        );
      } else if (match[2]) {
        // *italic* text
        parts.push(
          <em key={`italic-${match.index}`} className="italic text-gray-800">
            {match[2]}
          </em>
        );
      } else if (match[3]) {
        // `code` text
        parts.push(
          <code key={`code-${match.index}`} className="bg-gray-200 rounded px-1 py-0.5 text-xs font-mono">
            {match[3]}
          </code>
        );
      }

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    return parts.length > 0 ? parts : text;
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      // Prepare history: map current messages to {role, content}
      // Exclude messages that are errors or hidden
      const history = messages
        .filter(m => !m.isError)
        .map(m => ({ role: m.role, content: m.content }));

      const response = await varmaService.askQuestion(inputMessage, history);

      const assistantMessage = {
        role: 'assistant',
        content: response.answer || response.response || 'I apologize, but I couldn\'t generate a response.',
        sources: response.sources || [],
        varmaPoints: response.varma_points_explained || [],
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err.message || 'Failed to get response');
      const errorMessage = {
        role: 'assistant',
        content: 'I apologize, but I encountered an error processing your question. Please try again.',
        timestamp: new Date(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const suggestedQuestions = [
    'Explain about Utchi varmam and Vayu Varmam in detail',
    'Difference between Manibantha and Vishamanibantha Varmam',
    'What is the tamil literature associated with Udhira kaalam?',
    'What is the Pathognomic sign of Thivalai varmam?',
    'What is Natellu varmam in detail',
  ];

  const handleSuggestionClick = (question) => {
    setInputMessage(question);
    inputRef.current?.focus();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-[calc(100vh-8rem)]">
        {/* Header */}
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Ask About Varma Knowledge
          </h2>
          <p className="text-gray-600">
            Get detailed, grounded answers powered by our RAG-enhanced AI system
          </p>
        </div>

        {/* Chat Container */}
        <div className="bg-white rounded-2xl shadow-2xl flex flex-col h-[calc(100%-5rem)]">
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
              >
                <div className={`flex max-w-3xl ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  {/* Avatar */}
                  <div className={`flex-shrink-0 ${message.role === 'user' ? 'ml-3' : 'mr-3'}`}>
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        message.role === 'user'
                          ? 'bg-blue-600'
                          : message.isError
                          ? 'bg-red-500'
                          : 'bg-purple-600'
                      }`}
                    >
                      {message.role === 'user' ? (
                        <User className="w-6 h-6 text-white" />
                      ) : (
                        <Bot className="w-6 h-6 text-white" />
                      )}
                    </div>
                  </div>

                  {/* Message Content */}
                  <div className={`flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
                    <div
                      className={`rounded-2xl px-6 py-4 max-w-2xl ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : message.isError
                          ? 'bg-red-50 text-red-900 border border-red-200'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      {message.role === 'user' ? (
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">
                          {message.content}
                        </p>
                      ) : (
                        renderMarkdownContent(message.content)
                      )}

                      {/* Varma Points Info */}
                      {message.varmaPoints && message.varmaPoints.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-300">
                          <p className="text-xs font-semibold mb-2 text-gray-700">Varma Points Identified:</p>
                          <div className="space-y-2">
                            {message.varmaPoints.map((vp, idx) => (
                              <div key={idx} className="text-xs bg-white bg-opacity-50 p-2 rounded">
                                <p className="font-semibold text-gray-800">{vp.name}</p>
                                {vp.matched_symptoms.length > 0 && (
                                  <p className="text-gray-600 mt-1">
                                    Matched: {vp.matched_symptoms.join(', ')}
                                  </p>
                                )}
                                <p className="text-gray-500 text-xs mt-1">
                                  Confidence: {(vp.score * 100).toFixed(1)}%
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Sources */}
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-300">
                          <p className="text-xs font-semibold mb-2 text-gray-700">Sources:</p>
                          <div className="space-y-1">
                            {message.sources.map((source, idx) => (
                              <p key={idx} className="text-xs text-gray-600">
                                • {source}
                              </p>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Timestamp */}
                    <span className="text-xs text-gray-500 mt-1">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex justify-start animate-fade-in">
                <div className="flex">
                  <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center mr-3">
                    <Bot className="w-6 h-6 text-white" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <Loader className="w-5 h-5 animate-spin text-purple-600" />
                      <span className="text-gray-600">Thinking...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Questions */}
          {messages.length === 1 && !isLoading && (
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-2xl">
              <p className="text-sm font-medium text-gray-700 mb-3">💡 Try asking:</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(question)}
                    className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-xs text-gray-700 hover:bg-blue-50 hover:border-blue-400 transition-colors text-left"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Form */}
          <div className="border-t border-gray-200 p-4 rounded-b-2xl">
            {/* Error Message */}
            {error && (
              <div className="mb-3 p-3 bg-red-50 border-l-4 border-red-500 rounded flex items-start">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Input Form */}
            <form onSubmit={handleSendMessage} className="flex space-x-3">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  e.stopPropagation();
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(e);
                  }
                }}
                placeholder="Ask about Varma points, locations, applications..."
                className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-blue-500 focus:outline-none transition-colors bg-white"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
              >
                {isLoading ? (
                  <Loader className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RAGChat;