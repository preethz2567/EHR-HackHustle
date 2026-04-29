import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceArea } from 'recharts';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function HealthTrends({ data }) {
  // Mock time-series data for the last 6 months
  const trendData = [
    { month: 'Oct', hba1c: 7.2, systolic: 145, diastolic: 90, egfr: 45 },
    { month: 'Nov', hba1c: 7.0, systolic: 142, diastolic: 88, egfr: 43 },
    { month: 'Dec', hba1c: 6.8, systolic: 138, diastolic: 85, egfr: 42 },
    { month: 'Jan', hba1c: 6.5, systolic: 135, diastolic: 82, egfr: 40 },
    { month: 'Feb', hba1c: 6.2, systolic: 130, diastolic: 80, egfr: 38 },
    { month: 'Mar', hba1c: 5.9, systolic: 128, diastolic: 78, egfr: 36.29 }
  ];

  const TrendIndicator = ({ dataKey, invertGood = false }) => {
    const first = trendData[0][dataKey];
    const last = trendData[trendData.length - 1][dataKey];
    const diff = last - first;
    
    if (Math.abs(diff) < 0.5) return <Minus size={16} className="text-slate-400" />;
    
    const isUp = diff > 0;
    const isGood = invertGood ? !isUp : isUp;
    
    return isUp ? 
      <TrendingUp size={16} className={isGood ? 'text-green-500' : 'text-red-500'} /> : 
      <TrendingDown size={16} className={isGood ? 'text-green-500' : 'text-red-500'} />;
  };

  return (
    <div className="space-y-8">
      {/* HbA1c Chart */}
      <div className="card p-6 border border-slate-200">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-lg font-bold text-slate-800">HbA1c Trend</h3>
            <p className="text-sm text-slate-500">Target: &lt; 6.5%</p>
          </div>
          <div className="flex items-center gap-2 bg-slate-50 px-3 py-1 rounded-full border border-slate-200">
            <span className="text-sm font-semibold text-slate-700">6-Month Change:</span>
            <TrendIndicator dataKey="hba1c" invertGood={true} />
          </div>
        </div>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <LineChart data={trendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <YAxis domain={[5, 9]} axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
              <Legend />
              <ReferenceArea y1={5} y2={6.5} fill="#dcfce7" fillOpacity={0.3} />
              <Line type="monotone" dataKey="hba1c" name="HbA1c (%)" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Blood Pressure Chart */}
      <div className="card p-6 border border-slate-200">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-lg font-bold text-slate-800">Blood Pressure Trend</h3>
            <p className="text-sm text-slate-500">Target: &lt; 130/80 mmHg</p>
          </div>
          <div className="flex items-center gap-2 bg-slate-50 px-3 py-1 rounded-full border border-slate-200">
            <span className="text-sm font-semibold text-slate-700">6-Month Change:</span>
            <TrendIndicator dataKey="systolic" invertGood={true} />
          </div>
        </div>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <LineChart data={trendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <YAxis domain={[60, 160]} axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
              <Legend />
              <ReferenceArea y1={60} y2={130} fill="#dcfce7" fillOpacity={0.3} />
              <Line type="monotone" dataKey="systolic" name="Systolic" stroke="#ef4444" strokeWidth={3} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="diastolic" name="Diastolic" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* eGFR Chart */}
      <div className="card p-6 border border-slate-200">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h3 className="text-lg font-bold text-slate-800">eGFR Trend (Kidney Function)</h3>
            <p className="text-sm text-slate-500">Target: &gt; 60 mL/min</p>
          </div>
          <div className="flex items-center gap-2 bg-slate-50 px-3 py-1 rounded-full border border-slate-200">
            <span className="text-sm font-semibold text-slate-700">6-Month Change:</span>
            <TrendIndicator dataKey="egfr" invertGood={false} />
          </div>
        </div>
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <LineChart data={trendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <YAxis domain={[20, 100]} axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
              <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
              <Legend />
              <ReferenceArea y1={60} y2={100} fill="#dcfce7" fillOpacity={0.3} />
              <ReferenceArea y1={20} y2={45} fill="#fee2e2" fillOpacity={0.3} />
              <Line type="monotone" dataKey="egfr" name="eGFR" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
