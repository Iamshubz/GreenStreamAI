import React, { useState, useEffect } from 'react';
import { X, TrendingUp, TrendingDown, Wind, Droplets, Thermometer, AlertTriangle, Activity, Clock, Target, MapPin, ChevronRight } from 'lucide-react';

export default function CityDetailModal({ city, data, reports, onClose }) {
  const [historicalData, setHistoricalData] = useState([]);
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');

  // Get city-specific reports
  const cityReports = reports.filter(r => r.city === city);
  const latestReport = cityReports[0];

  const getAQILevel = (aqi) => {
    if (aqi < 50) return { label: 'Good', color: 'text-green-400', bg: 'bg-green-500/20' };
    if (aqi < 100) return { label: 'Moderate', color: 'text-yellow-400', bg: 'bg-yellow-500/20' };
    if (aqi < 200) return { label: 'Poor', color: 'text-orange-400', bg: 'bg-orange-500/20' };
    return { label: 'Hazardous', color: 'text-red-400', bg: 'bg-red-500/20' };
  };

  const aqiLevel = getAQILevel(data.aqi);
  const isCritical = data.aqi > 200 || data.co2 > 600;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-auto">
        {/* Modal Card */}
        <div className="relative backdrop-blur-xl bg-slate-900/90 rounded-3xl border border-white/20 shadow-2xl">
          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 bg-white/10 hover:bg-white/20 rounded-xl transition-all z-10 group"
          >
            <X className="w-6 h-6 text-gray-300 group-hover:text-white" />
          </button>

          {/* Header */}
          <div className="relative p-8 border-b border-white/10">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <MapPin className="w-8 h-8 text-cyan-400" />
                  <h2 className="text-4xl font-bold text-white">{city}</h2>
                </div>
                <div className="flex items-center gap-3 mt-4">
                  <span className={`px-4 py-2 ${aqiLevel.bg} ${aqiLevel.color} rounded-full text-sm font-semibold`}>
                    {aqiLevel.label}
                  </span>
                  {isCritical && (
                    <span className="px-4 py-2 bg-red-500/20 text-red-400 rounded-full text-sm font-semibold flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      Critical Alert
                    </span>
                  )}
                </div>
              </div>
              <div className="text-right">
                <div className="text-5xl font-bold text-white mb-1">{data.aqi}</div>
                <div className="text-gray-400">AQI Index</div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="p-8 space-y-6">
            {/* Current Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {/* Temperature */}
              <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Thermometer className="w-5 h-5 text-orange-400" />
                  <span className="text-gray-400 text-sm">Temperature</span>
                </div>
                <div className="text-3xl font-bold text-white">{data.temperature}°C</div>
              </div>

              {/* Humidity */}
              <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Droplets className="w-5 h-5 text-blue-400" />
                  <span className="text-gray-400 text-sm">Humidity</span>
                </div>
                <div className="text-3xl font-bold text-white">{data.humidity}%</div>
              </div>

              {/* CO2 */}
              <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Wind className="w-5 h-5 text-cyan-400" />
                  <span className="text-gray-400 text-sm">CO₂</span>
                </div>
                <div className="text-3xl font-bold text-white">{data.co2}</div>
                <div className="text-xs text-gray-500">ppm</div>
              </div>

              {/* Last Update */}
              <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="w-5 h-5 text-purple-400" />
                  <span className="text-gray-400 text-sm">Updated</span>
                </div>
                <div className="text-sm font-semibold text-white">
                  {new Date(data.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>

            {/* AI Explanation Section */}
            {latestReport && (
              <div className="backdrop-blur-xl bg-gradient-to-br from-purple-500/10 to-cyan-500/10 rounded-2xl border border-purple-500/30 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Activity className="w-6 h-6 text-purple-400" />
                  <h3 className="text-xl font-bold text-white">AI Analysis</h3>
                </div>
                
                {/* Explanation */}
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-400 mb-2">Current Situation:</h4>
                  <p className="text-white leading-relaxed">{latestReport.explanation}</p>
                </div>

                {/* Recommendation */}
                <div className="p-4 bg-white/5 rounded-xl border border-white/10">
                  <h4 className="text-sm font-semibold text-cyan-400 mb-2 flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    Recommended Actions:
                  </h4>
                  <p className="text-gray-300">{latestReport.recommendation}</p>
                </div>

                {/* Alert Details */}
                <div className="mt-4 flex items-center justify-between text-sm">
                  <span className="text-gray-400">
                    Alert Type: <span className="text-white font-semibold">{latestReport.alert_type}</span>
                  </span>
                  <span className="text-gray-400">
                    Severity: <span className={`font-semibold ${
                      latestReport.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'
                    }`}>{latestReport.severity}</span>
                  </span>
                </div>
              </div>
            )}

            {/* Historical Reports */}
            {cityReports.length > 1 && (
              <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <Activity className="w-6 h-6 text-cyan-400" />
                  Recent Alerts
                </h3>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {cityReports.slice(1, 6).map((report, idx) => (
                    <div key={idx} className="p-4 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-orange-400" />
                          <span className="text-sm font-semibold text-white">{report.alert_type}</span>
                        </div>
                        <span className="text-xs text-gray-400">
                          {new Date(report.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-300 line-clamp-2">{report.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Health Impact */}
            <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6">
              <h3 className="text-xl font-bold text-white mb-4">Health Impact</h3>
              <div className="space-y-3">
                {data.aqi > 200 && (
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-semibold text-white">High Risk</div>
                      <div className="text-sm text-gray-300">Prolonged exposure may cause respiratory issues. Avoid outdoor activities.</div>
                    </div>
                  </div>
                )}
                {data.co2 > 600 && (
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-semibold text-white">Elevated CO₂</div>
                      <div className="text-sm text-gray-300">Poor ventilation detected. Ensure adequate air circulation.</div>
                    </div>
                  </div>
                )}
                {data.aqi < 100 && data.co2 < 500 && (
                  <div className="flex items-start gap-3">
                    <Activity className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-semibold text-white">Good Conditions</div>
                      <div className="text-sm text-gray-300">Air quality is acceptable for most individuals.</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-white/10 flex items-center justify-between">
            <div className="text-sm text-gray-400">
              Last updated: {new Date(data.timestamp).toLocaleString()}
            </div>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-cyan-500 hover:bg-cyan-400 text-white font-semibold rounded-xl transition-all transform hover:scale-105"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
