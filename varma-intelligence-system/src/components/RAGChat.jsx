import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader, AlertCircle } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';
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
    'What are Varma points?',
    'How many Varma points are there in the human body?',
    'What is the difference between Varma and acupuncture?',
    'Which Varma points are used for headaches?',
    'Tell me about the history of Varma therapy',
  ];

  const handleSuggestionClick = (question) => {
    setInputMessage(question);
    inputRef.current?.focus();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-[calc(100vh-8rem)]">
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Ask About Varma Knowledge
          </h2>
          <p className="text-gray-600">
            Get detailed, grounded answers powered by our RAG-enhanced AI system
          </p>
        </div>

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
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${message.role === 'user'
                      ? 'bg-varma-primary'
                      : message.isError
                        ? 'bg-red-500'
                        : 'bg-purple-500'
                      }`}>
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
                      className={`rounded-2xl px-6 py-4 ${message.role === 'user'
                        ? 'bg-varma-primary text-white'
                        : message.isError
                          ? 'bg-red-50 text-red-900 border border-red-200'
                          : 'bg-gray-100 text-gray-900'
                        }`}
                    >
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">
                        {message.content}
                      </p>

                      {/* Sources */}
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-300">
                          <p className="text-xs font-semibold mb-2 text-gray-600">Sources:</p>
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

                    <span className="text-xs text-gray-500 mt-1">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start animate-fade-in">
                <div className="flex">
                  <div className="w-10 h-10 rounded-full bg-purple-500 flex items-center justify-center mr-3">
                    <Bot className="w-6 h-6 text-white" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <Loader className="w-5 h-5 animate-spin text-purple-500" />
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
            <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
              <p className="text-sm font-medium text-gray-700 mb-3">Suggested questions:</p>
              <div className="flex flex-wrap gap-2">
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(question)}
                    className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-100 hover:border-varma-primary transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Form */}
          <div className="border-t border-gray-200 p-4">
            {error && (
              <div className="mb-3 p-3 bg-red-50 border-l-4 border-red-500 rounded flex items-start">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            <form onSubmit={handleSendMessage} className="flex space-x-3">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => e.stopPropagation()}
                placeholder="Ask about Varma points, locations, applications..."
                className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-varma-primary focus:outline-none transition-colors"
                disabled={isLoading}
                style={{ pointerEvents: 'auto', position: 'relative', zIndex: 10 }}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="px-6 py-3 bg-varma-primary text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center"
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