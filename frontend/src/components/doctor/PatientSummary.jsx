import { Activity, Pill, FlaskConical, AlertTriangle } from 'lucide-react';

export default function PatientSummary({ data }) {
  if (!data) return null;

  return (
    <div className="data-grid">
      <div className="card p-5 border-t-4 border-t-slate-700">
        <div className="flex items-center gap-2 mb-4 text-slate-700">
          <Activity size={20} />
          <h3 className="font-semibold m-0 text-lg">Active Diagnoses</h3>
        </div>
        {data.diagnoses?.length > 0 ? (
          <ul className="space-y-3" style={{ listStyle: 'none', padding: 0 }}>
            {data.diagnoses.map((d, i) => (
              <li key={i} className="pb-3 border-b border-slate-100 last:border-0">
                <div className="font-medium text-slate-900">{d.name}</div>
                <div className="text-sm text-slate-500 mt-1">ICD-10: {d.code} • Since {d.date_of_diagnosis}</div>
              </li>
            ))}
          </ul>
        ) : <p className="text-sm text-slate-500">No active diagnoses</p>}
      </div>

      <div className="card p-5 border-t-4 border-t-blue-500">
        <div className="flex items-center gap-2 mb-4 text-blue-600">
          <Pill size={20} />
          <h3 className="font-semibold m-0 text-lg">Current Medications</h3>
        </div>
        {data.medications?.length > 0 ? (
          <ul className="space-y-3" style={{ listStyle: 'none', padding: 0 }}>
            {data.medications.map((m, i) => (
              <li key={i} className="pb-3 border-b border-slate-100 last:border-0">
                <div className="font-medium text-slate-900">{m.name} <span className="text-sm font-normal text-slate-500 ml-1">{m.dosage}</span></div>
                <div className="text-sm text-slate-500 mt-1">Started: {m.start_date}</div>
              </li>
            ))}
          </ul>
        ) : <p className="text-sm text-slate-500">No current medications</p>}
      </div>

      <div className="card p-5 border-t-4 border-t-emerald-500">
        <div className="flex items-center gap-2 mb-4 text-emerald-600">
          <FlaskConical size={20} />
          <h3 className="font-semibold m-0 text-lg">Recent Labs</h3>
        </div>
        {data.labs?.length > 0 ? (
          <ul className="space-y-3" style={{ listStyle: 'none', padding: 0 }}>
            {data.labs.map((l, i) => (
              <li key={i} className="pb-3 border-b border-slate-100 last:border-0 flex justify-between items-center">
                <div>
                  <div className="font-medium text-slate-900">{l.test_name}</div>
                  <div className="text-xs text-slate-500">{l.date}</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-slate-900">{l.value}</div>
                  <div className="text-xs text-slate-500">{l.reference_range}</div>
                </div>
              </li>
            ))}
          </ul>
        ) : <p className="text-sm text-slate-500">No recent labs</p>}
      </div>

      <div className="card p-5 border-t-4 border-t-red-500">
        <div className="flex items-center gap-2 mb-4 text-red-600">
          <AlertTriangle size={20} />
          <h3 className="font-semibold m-0 text-lg">Allergies</h3>
        </div>
        {data.allergies?.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {data.allergies.map((a, i) => (
              <span key={i} className="px-3 py-1 bg-red-50 text-red-700 rounded-full text-sm font-medium border border-red-100">
                {a}
              </span>
            ))}
          </div>
        ) : <p className="text-sm text-slate-500">No known allergies</p>}
      </div>
    </div>
  );
}
