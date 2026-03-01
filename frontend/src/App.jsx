import React, { useState, useEffect } from 'react';
import { AlertCircle, TrendingUp, CloudRain, Droplets, Wind, MapPin, LogOut } from 'lucide-react';

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
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-green-600 mb-2">🌱 GreenStream AI</h1>
          <p className="text-gray-600">Real-Time Environmental Monitoring</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter username"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter password"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            Sign In
          </button>
        </form>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg text-sm text-gray-700">
          <p className="font-semibold mb-1">Demo Credentials:</p>
          <p>Username: <span className="font-mono bg-white px-2 py-1 rounded">Shubham</span></p>
          <p>Password: <span className="font-mono bg-white px-2 py-1 rounded">Shubh@123</span></p>
        </div>
      </div>
    </div>
  );
}

// Main Dashboard Component
export default function Dashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [readings, setReadings] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [insight, setInsight] = useState(null);
  const [loading, setLoading] = useState(true);

  const API_BASE = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api`;

  // Fetch data every 3 seconds
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

  // Fetch AI insight when city is selected
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

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />;
  }

  const getAQIColor = (aqi) => {
    if (aqi < 50) return 'bg-green-100 border-green-300';
    if (aqi < 100) return 'bg-yellow-100 border-yellow-300';
    if (aqi < 200) return 'bg-orange-100 border-orange-300';
    return 'bg-red-100 border-red-300';
  };

  const getAQILabel = (aqi) => {
    if (aqi < 50) return '✅ Good';
    if (aqi < 100) return '⚠️ Moderate';
    if (aqi < 200) return '⚠️ Poor';
    return '🚨 Hazardous';
  };

  const getCO2Status = (co2) => {
    if (co2 < 600) return '✅ Normal';
    return '🚨 High';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-green-50 to-emerald-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-green-300 border-t-green-600 mx-auto mb-4"></div>
          <p className="text-green-700 font-semibold">Loading Environmental Data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-green-700 to-emerald-700 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold flex items-center gap-3">
              🌿 GreenStream AI
            </h1>
            <p className="text-green-100 mt-2">Real-Time Environmental Monitoring Dashboard</p>
          </div>
          <button
            onClick={() => setIsAuthenticated(false)}
            className="flex items-center gap-2 bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg transition-colors"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        {/* City Cards Grid */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <MapPin size={28} className="text-green-600" />
            Environmental Status by City
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Object.entries(readings).map(([city, data]) => (
              <div
                key={city}
                onClick={() => setSelectedCity(city)}
                className={`p-6 rounded-xl border-2 cursor-pointer transition-all transform hover:scale-105 ${
                  selectedCity === city
                    ? 'bg-white border-green-500 shadow-xl'
                    : `${getAQIColor(data.aqi)} border-opacity-50`
                }`}
              >
                <h3 className="text-xl font-bold text-gray-800 mb-4">{city}</h3>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2 text-gray-700">
                      <CloudRain size={20} />
                      <span>AQI</span>
                    </div>
                    <div>
                      <p className="font-bold text-lg">{data.aqi}</p>
                      <p className="text-sm text-gray-600">{getAQILabel(data.aqi)}</p>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2 text-gray-700">
                      <Wind size={20} />
                      <span>CO₂</span>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg">{data.co2} ppm</p>
                      <p className="text-sm text-gray-600">{getCO2Status(data.co2)}</p>
                    </div>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-gray-700">Temp</span>
                    <p className="font-bold">{data.temperature}°C</p>
                  </div>

                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2 text-gray-700">
                      <Droplets size={20} />
                      <span>Humidity</span>
                    </div>
                    <p className="font-bold">{data.humidity}%</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* AI Insight Panel */}
        {selectedCity && insight && (
          <section className="mb-12 bg-white rounded-xl shadow-lg p-8 border-l-4 border-green-600">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <TrendingUp size={28} className="text-green-600" />
              AI Environmental Intelligence - {selectedCity}
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-bold text-lg text-gray-800 mb-3">Current Alert</h3>
                <div className={`p-4 rounded-lg ${
                  insight.severity_level === 'critical' 
                    ? 'bg-red-50 border-2 border-red-300' 
                    : 'bg-yellow-50 border-2 border-yellow-300'
                }`}>
                  <p className="font-semibold text-gray-800">
                    CO₂: {insight.alert.co2} ppm | AQI: {insight.alert.aqi}
                  </p>
                  <p className="text-sm text-gray-600 mt-2">{insight.alert.timestamp}</p>
                </div>
              </div>

              <div>
                <h3 className="font-bold text-lg text-gray-800 mb-3">Analysis</h3>
                <p className="text-gray-700 leading-relaxed">{insight.explanation}</p>
              </div>

              <div className="md:col-span-2">
                <h3 className="font-bold text-lg text-gray-800 mb-3">Recommended Action</h3>
                <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4">
                  <p className="text-gray-700">{insight.recommendation}</p>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Recent Alerts */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            <AlertCircle size={28} className="text-red-600" />
            Recent Alerts
          </h2>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {alerts.slice(-10).reverse().map((alert, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border-l-4 ${
                  alert.severity === 'critical'
                    ? 'bg-red-50 border-red-500'
                    : 'bg-yellow-50 border-yellow-500'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-bold text-gray-800">{alert.city}</p>
                    <p className="text-sm text-gray-600">
                      CO₂: {alert.co2} ppm | AQI: {alert.aqi}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    alert.severity === 'critical'
                      ? 'bg-red-200 text-red-800'
                      : 'bg-yellow-200 text-yellow-800'
                  }`}>
                    {alert.severity.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Statistics */}
        <section>
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
            📊 Rolling Statistics (10-sec windows)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {stats.slice(-6).reverse().map((stat, idx) => (
              <div
                key={idx}
                className="bg-white rounded-xl shadow-md p-6 border-t-4 border-green-500"
              >
                <h3 className="text-lg font-bold text-gray-800 mb-4">{stat.city}</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Avg CO₂</p>
                    <p className="text-2xl font-bold text-green-600">{stat.avg_co2.toFixed(1)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Max CO₂</p>
                    <p className="text-2xl font-bold text-red-600">{stat.max_co2}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Avg AQI</p>
                    <p className="text-2xl font-bold text-orange-600">{stat.avg_aqi.toFixed(1)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Readings</p>
                    <p className="text-2xl font-bold text-blue-600">{stat.count}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 py-6 mt-16">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p>🌱 GreenStream AI - Real-Time Environmental Monitoring</p>
          <p className="text-sm mt-2">Built with React, Tailwind CSS, and Python</p>
        </div>
      </footer>
    </div>
  );
}
