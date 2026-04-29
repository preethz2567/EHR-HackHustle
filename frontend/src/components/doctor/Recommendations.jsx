import { Stethoscope, CheckSquare, CalendarClock } from 'lucide-react';

export default function Recommendations() {
  // Mock Orchestrator Output
  const orchestratorData = {
    clinical_summary: "Patient is a 68-year-old with a history of Ischemic Stroke (2016), Essential Hypertension, and Type 2 Diabetes. Recent trends show improving glycemic and blood pressure control, but a concerning downward trajectory in renal function (eGFR 36.29). There is an active contraindication with the current prescription of Lisinopril due to a documented ACE inhibitor allergy.",
    immediate_priorities: [
      "DISCONTINUE Lisinopril immediately due to documented ACE inhibitor allergy.",
      "Initiate alternative antihypertensive therapy (e.g., ARB or Calcium Channel Blocker) to maintain BP control.",
      "Schedule nephrology consult for progressive CKD Stage 3b management."
    ],
    key_risk_signals: [
      "eGFR has declined from 45 to 36.29 over the last 6 months.",
      "Current BP is 128/78, achieving target, but requires new medication strategy.",
      "HbA1c is excellently controlled at 5.9%."
    ],
    recommended_actions: [
      { timeframe: "Today", action: "Stop Lisinopril. Prescribe Amlodipine 5mg daily." },
      { timeframe: "Within 1 Week", action: "Follow-up metabolic panel to check potassium and creatinine post-medication change." },
      { timeframe: "Within 4 Weeks", action: "Nephrology evaluation for CKD progression." }
    ]
  };

  return (
    <div className="max-w-4xl space-y-8">
      {/* Clinical Summary */}
      <div className="bg-slate-800 text-white p-6 rounded-xl shadow-md">
        <div className="flex items-center gap-2 mb-3 text-blue-300">
          <Stethoscope size={24} />
          <h2 className="font-bold text-xl m-0">AI Clinical Synthesis</h2>
        </div>
        <p className="text-lg leading-relaxed font-medium">
          {orchestratorData.clinical_summary}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Immediate Priorities */}
        <div>
          <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2 border-b pb-2">
            <CheckSquare className="text-blue-600" size={20} /> Immediate Priorities
          </h3>
          <ol className="space-y-4 list-decimal list-inside">
            {orchestratorData.immediate_priorities.map((priority, i) => (
              <li key={i} className="font-semibold text-slate-800 pl-2">
                <span className="text-slate-700 font-medium">{priority}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Key Risk Signals */}
        <div>
          <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2 border-b pb-2">
            <Stethoscope className="text-blue-600" size={20} /> Key Risk Signals
          </h3>
          <ul className="space-y-3 list-disc list-inside">
            {orchestratorData.key_risk_signals.map((signal, i) => (
              <li key={i} className="text-slate-700">
                {signal}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Recommended Timeline */}
      <div className="mt-8">
        <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2 border-b pb-2">
          <CalendarClock className="text-blue-600" size={20} /> Action Timeline
        </h3>
        <div className="space-y-4">
          {orchestratorData.recommended_actions.map((item, i) => (
            <div key={i} className="flex gap-4 p-4 bg-white border border-slate-200 rounded-lg shadow-sm">
              <div className="w-32 flex-shrink-0 font-bold text-blue-700">
                {item.timeframe}
              </div>
              <div className="text-slate-800 font-medium">
                {item.action}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
