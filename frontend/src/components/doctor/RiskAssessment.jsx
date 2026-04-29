import { AlertOctagon, ShieldAlert, AlertTriangle } from 'lucide-react';

export default function RiskAssessment() {
  // Mock AI Agent Output
  const riskData = {
    immediate_risks: [
      { risk: 'High risk of recurrent ischemic stroke', severity: 'high', details: 'Patient has history of ischemic stroke (2016) with currently elevated HbA1c and poor BP control in recent history.' },
      { risk: 'Progressive CKD', severity: 'medium', details: 'eGFR shows downward trend over last 3 readings (currently 36.29 mL/min).' }
    ],
    drug_interactions: [
      { severity: 'high', description: 'Aspirin + Clopidogrel (Dual Antiplatelet Therapy)', notes: 'Appropriate for post-stroke, but monitor for bleeding risk.' }
    ],
    contraindications: [
      { item: 'ACE Inhibitors', reason: 'Documented allergy. Patient is currently on Lisinopril which is an ACE inhibitor. IMMEDIATE REVIEW REQUIRED.' }
    ]
  };

  return (
    <div className="max-w-4xl">
      <div className="mb-8">
        <h2 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
          <AlertOctagon className="text-red-600" /> Immediate Clinical Risks
        </h2>
        <div className="space-y-4">
          {riskData.immediate_risks.map((risk, i) => (
            <div key={i} className={`p-4 rounded-lg border-l-4 ${risk.severity === 'high' ? 'bg-red-50 border-red-500' : 'bg-orange-50 border-orange-400'}`}>
              <div className={`font-bold ${risk.severity === 'high' ? 'text-red-700' : 'text-orange-700'}`}>{risk.risk}</div>
              <p className="text-sm text-slate-700 mt-1">{risk.details}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card p-5 border border-slate-200">
          <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <ShieldAlert className="text-orange-500" size={20} /> Drug Interactions
          </h3>
          <ul className="space-y-4">
            {riskData.drug_interactions.map((interaction, i) => (
              <li key={i}>
                <div className="font-semibold text-slate-800">{interaction.description}</div>
                <div className="text-sm text-slate-600 mt-1 bg-slate-50 p-2 rounded">{interaction.notes}</div>
              </li>
            ))}
          </ul>
        </div>

        <div className="card p-5 border-2 border-red-200 bg-white shadow-sm">
          <h3 className="text-lg font-bold text-red-700 mb-4 flex items-center gap-2">
            <AlertTriangle size={20} /> Contraindications Detected
          </h3>
          <ul className="space-y-4">
            {riskData.contraindications.map((contra, i) => (
              <li key={i}>
                <div className="font-bold text-red-600 uppercase text-sm mb-1">{contra.item}</div>
                <div className="text-sm font-medium text-slate-800">{contra.reason}</div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
