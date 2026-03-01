import React, { useState, useEffect } from 'react';
import { AlertTriangle, Activity, TrendingUp, MapPin, Droplets, Wind, Thermometer, LogOut } from 'lucide-react';

// Login Component
function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username === 'Shubham' && password === 'Shubh@123') {
      onLogin();
      setError('');
    } else {
      setError('Invalid credentials. Use: Shubham / Shubh@123');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white/10 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-2">
            🌍 GreenStream AI
          </h1>
          <p className="text-gray-300">Smart City Command Center</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyan-500 focus:border-transparent backdrop-blur-sm"
              placeholder="Enter username"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyan-500 focus:border-transparent backdrop-blur-sm"
              placeholder="Enter password"
              required
            />
          </div>

          {error && (
            <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-3 rounded-xl text-sm backdrop-blur-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-semibold py-3 rounded-xl transition-all transform hover:scale-105"
          >
            Access Command Center
          </button>
        </form>

        <div className="mt-6 p-4 bg-white/5 backdrop-blur-sm rounded-xl text-sm text-gray-300 border border-white/10">
          <p className="font-semibold mb-1">Demo Credentials:</p>
          <p>Username: <span className="font-mono bg-white/10 px-2 py-1 rounded">Shubham</span></p>
          <p>Password: <span className="font-mono bg-white/10 px-2 py-1 rounded">Shubh@123</span></p>
        </div>
      </div>
    </div>
  );
}

// Circular AQI Gauge Component
function AQIGauge({ value, size = 120 }) {
  const getColor = (aqi) => {
    if (aqi < 50) return '#10b981';
    if (aqi < 100) return '#f59e0b';
    if (aqi < 200) return '#ef4444';
    return '#dc2626';
  };

  const percentage = Math.min((value / 500) * 100, 100);
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r="45"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth="8"
          fill="none"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r="45"
          stroke={getColor(value)}
          strokeWidth="8"
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-1000"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold text-white">{value}</span>
        <span className="text-xs text-gray-400">AQI</span>
      </div>
    </div>
  );
}

// Main Dashboard
export default function Dashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [readings, setReadings] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [insight, setInsight] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());

  const API_BASE = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api`;

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch data
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const fetchData = async () => {
      try {
        const dashboardRes = await fetch(`${API_BASE}/dashboard`);
        const dashboard = await dashboardRes.json();
        setReadings(dashboard.readings || {});
        setAlerts(dashboard.recent_alerts || []);
        setStats(dashboard.recent_stats || []);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [API_BASE, isAuthenticated]);

  // Fetch AI insight
  useEffect(() => {
    if (!isAuthenticated || !selectedCity) return;
    
    const fetchInsight = async () => {
      try {
        const res = await fetch(`${API_BASE}/insights/${selectedCity}`);
        const data = await res.json();
        setInsight(data);
      } catch (error) {
        console.error('Error fetching insight:', error);
      }
    };
    fetchInsight();
  }, [API_BASE, selectedCity, isAuthenticated]);

  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-cyan-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-cyan-400 font-semibold text-lg">Initializing Command Center...</p>
        </div>
      </div>
    );
  }

  const cityArray = Object.entries(readings);
  const sortedByAQI = [...cityArray].sort((a, b) => b[1].aqi - a[1].aqi);

  const getHealthScore = (data) => {
    const aqiScore = Math.max(0, 100 - (data.aqi / 5));
    const co2Score = Math.max(0, 100 - ((data.co2 - 400) / 5));
    return Math.round((aqiScore + co2Score) / 2);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 flex items-center gap-3">
              <Activity className="text-cyan-400" size={32} />
              GreenStream AI Command Center
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              {currentTime.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', dateStyle: 'full', timeStyle: 'medium' })}
            </p>
          </div>
          <button
            onClick={() => setIsAuthenticated(false)}
            className="flex items-center gap-2 bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg transition-colors text-white border border-white/20"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 animate-fadeIn">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Cities</p>
                <p className="text-4xl font-bold text-white mt-1">{cityArray.length}</p>
              </div>
              <MapPin className="text-cyan-400" size={40} />
            </div>
          </div>
          
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 animate-fadeIn">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Critical Alerts</p>
                <p className="text-4xl font-bold text-red-400 mt-1">{alerts.filter(a => a.severity === 'critical').length}</p>
              </div>
              <AlertTriangle className="text-red-400 animate-pulse" size={40} />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 animate-fadeIn">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Avg AQI</p>
                <p className="text-4xl font-bold text-orange-400 mt-1">
                  {cityArray.length > 0 ? Math.round(cityArray.reduce((acc, [, data]) => acc + data.aqi, 0) / cityArray.length) : 'N/A'}
                </p>
              </div>
              <Activity className="text-orange-400" size={40} />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 animate-fadeIn">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Avg Temp</p>
                <p className="text-4xl font-bold text-blue-400 mt-1">
                  {cityArray.length > 0 ? Math.round(cityArray.reduce((acc, [, data]) => acc + data.temperature, 0) / cityArray.length) : 'N/A'}°C
                </p>
              </div>
              <Thermometer className="text-blue-400" size={40} />
            </div>
          </div>
        </div>

        {/* City Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {cityArray.map(([city, data]) => {
            const healthScore = getHealthScore(data);
            return (
              <div
                key={city}
                className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 hover:border-cyan-500/50 transition-all cursor-pointer transform hover:scale-105 animate-fadeIn"
                onClick={() => setSelectedCity(city)}
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-white flex items-center gap-2">
                      <MapPin size={20} className="text-cyan-400" />
                      {city}
                    </h3>
                    <p className="text-sm text-gray-400">{new Date(data.timestamp).toLocaleTimeString()}</p>
                  </div>
                </div>

                <div className="flex justify-center mb-4">
                  <AQIGauge value={data.aqi} size={100} />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400 flex items-center gap-1">
                      <Thermometer size={16} /> Temp
                    </span>
                    <span className="text-white font-semibold">{data.temperature}°C</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400 flex items-center gap-1">
                      <Wind size={16} /> CO₂
                    </span>
                    <span className="text-white font-semibold">{data.co2} ppm</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400 flex items-center gap-1">
                      <Droplets size={16} /> Humidity
                    </span>
                    <span className="text-white font-semibold">{data.humidity}%</span>
                  </div>
                </div>

                {/* Health Score */}
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-gray-400">Health Score</span>
                    <span className="text-sm font-bold text-white">{healthScore}/100</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        healthScore > 70 ? 'bg-green-500' : healthScore > 40 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${healthScore}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Rankings Panel */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="text-red-400" />
            Most Polluted Cities
          </h2>
          <div className="space-y-3">
            {sortedByAQI.slice(0, 5).map(([city, data], index) => (
              <div key={city} className="flex items-center justify-between bg-white/5 rounded-xl p-4 backdrop-blur-sm">
                <div className="flex items-center gap-4">
                  <span className="text-2xl font-bold text-gray-500">#{index + 1}</span>
                  <span className="text-white font-semibold">{city}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-orange-400 font-bold">AQI {data.aqi}</span>
                  <span className="text-gray-400">CO₂ {data.co2} ppm</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Insight Modal */}
        {selectedCity && insight && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50" onClick={() => setSelectedCity(null)}>
            <div className="bg-slate-900/95 backdrop-blur-xl rounded-3xl p-8 max-w-2xl w-full border border-cyan-500/30 shadow-2xl" onClick={(e) => e.stopPropagation()}>
              <h3 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-6 flex items-center gap-2">
                <Activity className="text-cyan-400" size={32} />
                AI Analysis: {selectedCity}
              </h3>
              
              {/* Alert Details */}
              <div className="bg-white/5 rounded-xl p-4 mb-4 border border-white/10">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">AQI Level:</span>
                    <span className="text-orange-400 font-bold ml-2">{insight.alert?.aqi || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">CO₂:</span>
                    <span className="text-white font-bold ml-2">{insight.alert?.co2 || 'N/A'} ppm</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Temperature:</span>
                    <span className="text-white font-bold ml-2">{insight.alert?.temperature || 'N/A'}°C</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Humidity:</span>
                    <span className="text-white font-bold ml-2">{insight.alert?.humidity || 'N/A'}%</span>
                  </div>
                </div>
              </div>

              {/* AI Explanation */}
              <div className="mb-4">
                <h4 className="text-lg font-semibold text-cyan-400 mb-2">🤖 AI Explanation</h4>
                <div className="bg-white/5 rounded-xl p-6 text-gray-300 leading-relaxed border border-white/10">
                  {insight.explanation || 'Analyzing environmental data...'}
                </div>
              </div>

              {/* AI Recommendation */}
              {insight.recommendation && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-green-400 mb-2">💡 Recommendations</h4>
                  <div className="bg-green-500/10 rounded-xl p-6 text-gray-300 leading-relaxed border border-green-500/20">
                    {insight.recommendation}
                  </div>
                </div>
              )}

              {/* Severity Badge */}
              {insight.severity_level && (
                <div className="mb-6">
                  <span className={`inline-block px-4 py-2 rounded-full text-sm font-semibold ${
                    insight.severity_level === 'critical' 
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                      : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                  }`}>
                    {insight.severity_level === 'critical' ? '🚨 Critical Alert' : '⚠️ Warning'}
                  </span>
                </div>
              )}

              <button
                onClick={() => setSelectedCity(null)}
                className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-semibold py-3 rounded-xl transition-all transform hover:scale-105"
              >
                Close Analysis
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
