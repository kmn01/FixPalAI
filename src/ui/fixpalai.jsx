import React, { useState } from 'react';
import { Camera, Mic, Upload, Search, Settings, MessageSquare, Wrench, Snowflake, Zap, Hammer, AlertTriangle, CheckCircle, Clock, TrendingUp } from 'lucide-react';

const FixPalAI = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [showDiagnosis, setShowDiagnosis] = useState(false);

  const quickActions = [
    { icon: Wrench, label: 'Plumbing', category: 'plumbing', iconClass: 'text-blue-500' },
    { icon: Snowflake, label: 'HVAC', category: 'hvac', iconClass: 'text-cyan-500' },
    { icon: Zap, label: 'Electrical', category: 'electrical', iconClass: 'text-yellow-500' },
    { icon: Hammer, label: 'Appliances', category: 'appliance', iconClass: 'text-purple-500' }
  ];

  const recentChats = [
    { title: 'HVAC condenser issue', time: '15 min ago', category: 'HVAC' },
    { title: 'Leaky faucet repair', time: '1 hour ago', category: 'Plumbing' },
    { title: 'Outlet not working', time: '2 hours ago', category: 'Electrical' }
  ];

  const repairSteps = [
    "Turn off power at the circuit breaker and verify with a voltage tester",
    "Remove the access panel on the condenser unit",
    "Disconnect the electrical connections to the fan motor",
    "Remove the mounting bolts securing the fan motor",
    "Install the new fan motor and reconnect all wiring",
    "Replace the access panel and restore power",
    "Test the system to ensure proper operation"
  ];

  const handleQuickAction = (category) => {
    setInputValue(`I need help with a ${category} issue`);
  };

  const handleSubmit = () => {
    if (inputValue.trim() || selectedImage) {
      setMessages([...messages, { role: 'user', content: inputValue, image: selectedImage }]);
      setShowDiagnosis(true);
      setInputValue('');
      setSelectedImage(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-full w-80 bg-white shadow-xl border-r border-gray-200 overflow-y-auto">
        {/* Logo Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white">
          <div className="flex items-center space-x-3">
            <Wrench className="w-8 h-8" />
            <div>
              <h1 className="text-2xl font-bold">FixPalAI</h1>
              <p className="text-sm text-indigo-100">AI Technician Copilot</p>
            </div>
          </div>
        </div>

        {/* Knowledge Base Status */}
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">Knowledge Base</h3>
            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-semibold rounded-full flex items-center">
              <CheckCircle className="w-3 h-3 mr-1" />
              Connected
            </span>
          </div>
          <p className="text-sm text-gray-600 mb-3">3,247 repair guides loaded</p>
          <button className="w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm font-medium transition-colors flex items-center justify-center">
            <Settings className="w-4 h-4 mr-2" />
            Manage Sources
          </button>
        </div>

        {/* Upload Section */}
        <div className="p-6 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Upload Materials</h3>
          <label className="block w-full px-4 py-8 border-2 border-dashed border-gray-300 rounded-lg text-center cursor-pointer hover:border-indigo-500 hover:bg-indigo-50 transition-all">
            <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <span className="text-sm text-gray-600">Drop files or click to upload</span>
            <input type="file" className="hidden" multiple accept=".pdf,.docx,.txt" />
          </label>
        </div>

        {/* Recent Conversations */}
        <div className="p-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Recent Conversations</h3>
          <div className="space-y-2">
            {recentChats.map((chat, idx) => (
              <div key={idx} className="p-3 rounded-lg hover:bg-gray-50 cursor-pointer border-l-4 border-transparent hover:border-indigo-500 transition-all">
                <div className="flex items-start">
                  <MessageSquare className="w-4 h-4 text-gray-400 mt-1 mr-2 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{chat.title}</p>
                    <p className="text-xs text-gray-500 mt-1 flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {chat.time}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Footer */}
        <div className="p-6 border-t border-gray-100 bg-gray-50">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-indigo-600">247</p>
              <p className="text-xs text-gray-500">Queries</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">89%</p>
              <p className="text-xs text-gray-500">Resolved</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">3.2s</p>
              <p className="text-xs text-gray-500">Avg Time</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-80 p-8">
        {/* Welcome Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white mb-8 shadow-lg">
          <h1 className="text-4xl font-bold mb-2">👋 Welcome to FixPalAI</h1>
          <p className="text-lg text-indigo-100">Get instant repair guidance for any field service issue</p>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🚀 Quick Start</h2>
          <div className="grid grid-cols-4 gap-4">
            {quickActions.map((action, idx) => {
              const Icon = action.icon;
              return (
                <button
                  key={idx}
                  onClick={() => handleQuickAction(action.category)}
                  className="bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-indigo-500 hover:shadow-lg transition-all transform hover:-translate-y-1 group"
                >
                  <Icon className={`w-12 h-12 mx-auto mb-3 ${action.iconClass} group-hover:scale-110 transition-transform`} />
                  <p className="font-semibold text-gray-900">{action.label}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">💬 Describe Your Issue</h2>
          
          <div className="grid grid-cols-3 gap-6">
            {/* Text Input */}
            <div className="col-span-2">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Describe the issue in detail... e.g., 'My HVAC unit is making a loud grinding noise'"
                className="w-full h-32 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none resize-none transition-all"
              />
            </div>

            {/* Image Upload */}
            <div>
              <label className="block w-full h-32 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-indigo-500 hover:bg-indigo-50 transition-all">
                {selectedImage ? (
                  <img src={URL.createObjectURL(selectedImage)} alt="Preview" className="w-full h-full object-cover rounded-xl" />
                ) : (
                  <div className="flex flex-col items-center justify-center h-full">
                    <Camera className="w-8 h-8 text-gray-400 mb-2" />
                    <span className="text-sm text-gray-600">Upload Photo</span>
                  </div>
                )}
                <input
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={(e) => setSelectedImage(e.target.files[0])}
                />
              </label>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 mt-6">
            <button
              onClick={handleSubmit}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-xl transition-all flex items-center justify-center shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <Search className="w-5 h-5 mr-2" />
              Get Repair Guide
            </button>
            <button className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 px-6 rounded-xl transition-all flex items-center justify-center">
              <Mic className="w-5 h-5 mr-2" />
              Voice
            </button>
            <button
              onClick={() => {
                setInputValue('');
                setSelectedImage(null);
                setMessages([]);
                setShowDiagnosis(false);
              }}
              className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 px-6 rounded-xl transition-all"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Diagnosis Display */}
        {showDiagnosis && (
          <div className="space-y-6">
            {/* Analysis Card */}
            <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-green-500 overflow-hidden">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">🤖 FixPalAI Analysis</h3>
                  <p className="text-gray-600">Issue identified and repair plan generated</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-500" />
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Detected Issue</p>
                  <p className="font-semibold text-gray-900">HVAC Condenser Fan Motor Failure</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Severity</p>
                  <span className="inline-block px-3 py-1 bg-yellow-100 text-yellow-700 text-sm font-semibold rounded-full">Medium</span>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Estimated Time</p>
                  <p className="font-semibold text-gray-900">45 minutes</p>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-gray-500">AI Confidence</p>
                  <p className="text-sm font-semibold text-gray-900">87%</p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-gradient-to-r from-green-500 to-green-400 h-2 rounded-full" style={{width: '87%'}}></div>
                </div>
                <p className="text-xs text-gray-500 mt-2">High match with known issue DB-4782</p>
              </div>
            </div>

            {/* Safety Warning */}
            <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-xl p-6 flex items-start">
              <AlertTriangle className="w-6 h-6 text-yellow-600 mr-4 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-bold text-yellow-900 mb-2">⚠️ SAFETY ALERT</h4>
                <p className="text-yellow-800 text-sm">
                  This repair involves electrical components. Turn off the circuit breaker before proceeding.
                  Consider professional help if you're not comfortable working with electricity.
                </p>
              </div>
            </div>

            {/* Repair Steps */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6">🔧 Step-by-Step Repair Guide</h3>
              
              <div className="space-y-4">
                {repairSteps.map((step, idx) => (
                  <div key={idx} className="flex items-start p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-all">
                    <div className="flex-shrink-0 w-8 h-8 bg-indigo-600 text-white rounded-full flex items-center justify-center font-bold mr-4">
                      {idx + 1}
                    </div>
                    <p className="text-gray-700 flex-1 pt-1">{step}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Tools and Parts */}
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h4 className="text-lg font-bold text-gray-900 mb-4">🛠️ Tools Needed</h4>
                <ul className="space-y-2">
                  {['Screwdriver set', 'Socket wrench', 'Voltage tester', 'Wire strippers'].map((tool, idx) => (
                    <li key={idx} className="flex items-center text-gray-700">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                      {tool}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h4 className="text-lg font-bold text-gray-900 mb-4">📦 Parts Required</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">Condenser fan motor</span>
                    <span className="font-bold text-indigo-600">$85-120</span>
                  </div>
                  <div className="text-gray-600 text-sm">Wire connectors (if needed)</div>
                  <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-all mt-4">
                    🛒 Find Parts Online
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!showDiagnosis && messages.length === 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <div className="max-w-2xl mx-auto">
              <div className="text-6xl mb-4">🔧</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-3">Ready to Help!</h3>
              <p className="text-gray-600 mb-8">
                Describe your issue above or select a category to get instant repair guidance from AI
              </p>

              <div className="text-left">
                <h4 className="font-semibold text-gray-900 mb-4">💡 Try these examples:</h4>
                <div className="space-y-2">
                  {[
                    "My water heater is leaking from the bottom",
                    "HVAC unit won't turn on and thermostat shows error E3",
                    "Dishwasher not draining water properly",
                    "Circuit breaker keeps tripping when I use the microwave"
                  ].map((example, idx) => (
                    <button
                      key={idx}
                      onClick={() => setInputValue(example)}
                      className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-indigo-50 hover:border-indigo-300 border border-gray-200 rounded-lg transition-all text-sm text-gray-700"
                    >
                      💬 {example}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FixPalAI;