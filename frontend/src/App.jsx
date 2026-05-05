import React, { useState, useEffect, useRef } from 'react';
import { Search, UploadCloud, Activity, AlertCircle, CheckCircle2, ChevronRight, PieChart, Info, Droplet, Flame, Leaf, Hexagon, X, Image as ImageIcon } from 'lucide-react';

const API_BASE = 'http://127.0.0.1:5000/api';

export default function App() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedImage, setUploadedImage] = useState(null);
  
  const [showManual, setShowManual] = useState(false);
  const [manualFeatures, setManualFeatures] = useState({
    energy_100g: 0, sugars_100g: 0, fat_100g: 0, proteins_100g: 0,
    salt_100g: 0, carbohydrates_100g: 0, fiber_100g: 0, saturated_fat_100g: 0
  });

  const handleSearch = async (val) => {
    setQuery(val);
    if (val.length > 2) {
      try {
        const res = await fetch(`${API_BASE}/search?q=${val}`);
        const data = await res.json();
        setSuggestions(data);
      } catch (err) {
        console.error("Search error:", err);
      }
    } else {
      setSuggestions([]);
    }
  };

  const analyzeFood = async (product) => {
    setLoading(true);
    setSuggestions([]);
    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          features: product.features,
          ingredients: product.ingredients || product.name
        })
      });
      const data = await res.json();
      setResult({ ...data, name: product.name, image: uploadedImage });
    } catch (err) {
      alert("Error analyzing food. Check if backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleManualSubmit = () => {
    analyzeFood({ name: "Custom Entry", features: manualFeatures, ingredients: "" });
  };

  // Drag and drop handlers (Mock UI for now as backend needs image processing setup)
  const onDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const onDragLeave = () => setIsDragging(false);
  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setUploadedImage(URL.createObjectURL(file));
      // Mock analyzing an uploaded image
      setTimeout(() => {
        analyzeFood({
          name: file.name.split('.')[0],
          features: { energy_100g: 250, sugars_100g: 10, fat_100g: 12, proteins_100g: 5, salt_100g: 0.5, carbohydrates_100g: 30, fiber_100g: 2, saturated_fat_100g: 4 },
          ingredients: "Sample ingredients from image"
        });
      }, 1500);
    }
  };

  const getColorTheme = (pred) => {
    if (pred === 'Healthy') return { text: 'text-emerald-500', bg: 'bg-emerald-500', lightBg: 'bg-emerald-50', border: 'border-emerald-200' };
    if (pred === 'Moderate') return { text: 'text-amber-500', bg: 'bg-amber-500', lightBg: 'bg-amber-50', border: 'border-amber-200' };
    return { text: 'text-rose-500', bg: 'bg-rose-500', lightBg: 'bg-rose-50', border: 'border-rose-200' };
  };

  const theme = result ? getColorTheme(result.prediction) : getColorTheme('Healthy');

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 font-sans selection:bg-orange-200 overflow-x-hidden">
      {/* Navbar */}
      <nav className="bg-white/70 backdrop-blur-md sticky top-0 z-50 border-b border-slate-100 shadow-sm">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3 cursor-pointer">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-rose-500 rounded-2xl flex items-center justify-center shadow-lg shadow-orange-200/50">
              <Activity className="text-white w-6 h-6" />
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-800 to-slate-500">
              NutriAI
            </span>
          </div>
          <div className="hidden md:flex gap-8 text-sm font-semibold text-slate-500">
            <a href="#" className="text-slate-900">Analyzer</a>
            <a href="#" className="hover:text-slate-900 transition-colors">History</a>
            <a href="#" className="hover:text-slate-900 transition-colors">About Model</a>
          </div>
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-6 py-12 space-y-12">
        {/* Input Section */}
        <section className="bg-white p-8 md:p-12 rounded-[2rem] shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 relative overflow-hidden group transition-all duration-500 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)]">
          <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-gradient-to-br from-orange-50 to-rose-50 rounded-full blur-3xl opacity-50 pointer-events-none"></div>
          
          <div className="text-center max-w-2xl mx-auto mb-10 relative z-10">
            <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 mb-4 tracking-tight">What's in your food?</h1>
            <p className="text-lg text-slate-500">Search our database, enter nutrients manually, or upload a photo to get an instant AI health analysis.</p>
          </div>

          <div className="max-w-3xl mx-auto space-y-6 relative z-10">
            {/* Search Bar */}
            <div className="relative">
              <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                <Search className="text-slate-400 w-6 h-6" />
              </div>
              <input
                type="text"
                placeholder="Search for a food item..."
                className="w-full pl-14 pr-6 py-5 bg-slate-50 border-2 border-slate-100 rounded-2xl text-lg focus:outline-none focus:border-orange-400 focus:ring-4 focus:ring-orange-100 transition-all shadow-inner"
                value={query}
                onChange={(e) => handleSearch(e.target.value)}
              />
              {/* Dropdown */}
              {suggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-3 bg-white rounded-2xl shadow-2xl border border-slate-100 overflow-hidden z-50 animate-in slide-in-from-top-2">
                  {suggestions.map((s, i) => (
                    <button
                      key={i}
                      className="w-full px-6 py-4 text-left hover:bg-slate-50 flex items-center justify-between group transition-colors border-b border-slate-50 last:border-0"
                      onClick={() => analyzeFood(s)}
                    >
                      <span className="font-semibold text-slate-700 group-hover:text-orange-500 transition-colors">{s.name}</span>
                      <ChevronRight className="text-slate-300 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Drag & Drop Upload */}
            <div 
              onDragOver={onDragOver} onDragLeave={onDragLeave} onDrop={onDrop}
              className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${isDragging ? 'border-orange-500 bg-orange-50' : 'border-slate-200 hover:border-orange-300 hover:bg-slate-50'}`}
            >
              <UploadCloud className={`w-12 h-12 mx-auto mb-4 ${isDragging ? 'text-orange-500' : 'text-slate-400'}`} />
              <p className="text-slate-600 font-medium">Drag & drop an image of a nutrition label, or <span className="text-orange-500 cursor-pointer hover:underline">browse</span></p>
              <p className="text-slate-400 text-sm mt-2">Supports JPG, PNG (Mock Feature)</p>
            </div>

            {/* Manual Toggle */}
            <div className="text-center">
               <button onClick={() => setShowManual(!showManual)} className="text-sm font-bold text-slate-400 hover:text-slate-600 uppercase tracking-widest transition-colors">
                 {showManual ? 'Hide Manual Entry' : 'Manual Nutrition Entry'}
               </button>
            </div>

            {showManual && (
              <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 animate-in fade-in zoom-in-95 duration-300">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.keys(manualFeatures).map(key => (
                    <div key={key}>
                      <label className="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-2">{key.replace('_100g', '').replace('_', ' ')}</label>
                      <input
                        type="number"
                        className="w-full p-3 bg-white rounded-xl border border-slate-200 focus:border-orange-400 focus:ring-2 focus:ring-orange-100 outline-none transition-all"
                        value={manualFeatures[key]}
                        onChange={(e) => setManualFeatures({...manualFeatures, [key]: parseFloat(e.target.value) || 0})}
                      />
                    </div>
                  ))}
                </div>
                <button onClick={handleManualSubmit} className="mt-6 w-full py-4 bg-slate-900 text-white rounded-xl font-bold hover:bg-orange-500 transition-colors shadow-lg hover:shadow-orange-200">
                  Analyze Manual Data
                </button>
              </div>
            )}
          </div>
        </section>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 animate-pulse">
            <div className="w-16 h-16 border-4 border-slate-200 border-t-orange-500 rounded-full animate-spin mb-6"></div>
            <p className="text-slate-500 font-medium">AI is analyzing nutrition data...</p>
          </div>
        )}

        {/* Results Section */}
        {result && !loading && (
          <div className="space-y-8 animate-in slide-in-from-bottom-8 duration-700">
            
            {/* Top Overview Card */}
            <section className={`p-8 md:p-10 rounded-[2.5rem] border shadow-xl relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-10 ${theme.lightBg} ${theme.border}`}>
              <div className="absolute top-0 right-0 w-[40rem] h-[40rem] bg-white opacity-40 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3 pointer-events-none"></div>
              
              <div className="relative z-10 flex-1 space-y-6 text-center md:text-left">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-full shadow-sm font-bold text-sm tracking-wide">
                  <span className={`w-3 h-3 rounded-full ${theme.bg} animate-pulse`}></span>
                  <span className={theme.text}>{result.prediction.toUpperCase()}</span>
                </div>
                <h2 className="text-4xl md:text-5xl font-black text-slate-900">{result.name}</h2>
                <p className="text-lg text-slate-600 leading-relaxed max-w-xl">{result.explanation}</p>
                
                {/* Confidence Bars */}
                <div className="pt-4 space-y-3 max-w-md">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">AI Confidence Score</p>
                  <div className="flex w-full h-3 bg-white rounded-full overflow-hidden shadow-inner">
                    <div className="bg-emerald-500 h-full transition-all duration-1000" style={{ width: `${result.confidence.Healthy}%` }}></div>
                    <div className="bg-amber-400 h-full transition-all duration-1000" style={{ width: `${result.confidence.Moderate}%` }}></div>
                    <div className="bg-rose-500 h-full transition-all duration-1000" style={{ width: `${result.confidence.Unhealthy}%` }}></div>
                  </div>
                  <div className="flex justify-between text-xs font-semibold text-slate-500">
                    <span className="text-emerald-600">{result.confidence.Healthy}% Healthy</span>
                    <span className="text-amber-600">{result.confidence.Moderate}% Moderate</span>
                    <span className="text-rose-600">{result.confidence.Unhealthy}% Unhealthy</span>
                  </div>
                </div>
              </div>

              {/* Circular Gauge */}
              <div className="relative z-10 shrink-0 bg-white p-6 rounded-[2rem] shadow-lg shadow-slate-200/50 flex flex-col items-center">
                <div className="relative w-40 h-40 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="12" fill="transparent" className="text-slate-100" />
                    <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="12" fill="transparent" strokeLinecap="round"
                      strokeDasharray={2 * Math.PI * 70} 
                      strokeDashoffset={2 * Math.PI * 70 * (1 - result.health_score / 100)} 
                      className={`${theme.text} transition-all duration-1000 ease-out`} 
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-5xl font-black text-slate-800">{result.health_score}</span>
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">Score</span>
                  </div>
                </div>
              </div>
            </section>

            {/* Bottom Grid: Nutrition & Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* Nutrition Grid (Spans 2 columns) */}
              <section className="lg:col-span-2 bg-white p-8 rounded-[2rem] border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] hover:shadow-[0_4px_20px_rgb(0,0,0,0.06)] transition-all">
                <div className="flex items-center gap-3 mb-8">
                  <div className="p-2 bg-blue-50 text-blue-500 rounded-xl"><PieChart w={20} h={20} /></div>
                  <h3 className="text-xl font-bold text-slate-800">Nutritional Values <span className="text-sm font-normal text-slate-400 ml-2">(per 100g)</span></h3>
                </div>
                
                <div className="grid grid-cols-2 gap-6">
                  <NutritionBar label="Energy" value={result.nutritional_breakdown.calories} max={800} unit="kcal" icon={<Flame size={18}/>} color="bg-orange-500" />
                  <NutritionBar label="Protein" value={result.nutritional_breakdown.protein} max={30} unit="g" icon={<Hexagon size={18}/>} color="bg-emerald-500" />
                  <NutritionBar label="Fat" value={result.nutritional_breakdown.fat} max={50} unit="g" icon={<Droplet size={18}/>} color="bg-rose-400" />
                  <NutritionBar label="Carbs" value={result.nutritional_breakdown.carbs} max={100} unit="g" icon={<Leaf size={18}/>} color="bg-amber-400" />
                  <NutritionBar label="Sugars" value={result.nutritional_breakdown.sugar} max={50} unit="g" icon={<Hexagon size={18}/>} color="bg-rose-500" isWarning={result.nutritional_breakdown.sugar > 15} />
                  <NutritionBar label="Fiber" value={result.nutritional_breakdown.fiber} max={20} unit="g" icon={<Leaf size={18}/>} color="bg-emerald-400" />
                </div>
              </section>

              {/* Insights / NLP Warnings */}
              <section className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] hover:shadow-[0_4px_20px_rgb(0,0,0,0.06)] transition-all flex flex-col">
                <div className="flex items-center gap-3 mb-8">
                  <div className="p-2 bg-purple-50 text-purple-500 rounded-xl"><Info w={20} h={20} /></div>
                  <h3 className="text-xl font-bold text-slate-800">Ingredient Insights</h3>
                </div>
                
                <div className="space-y-4 flex-1 overflow-y-auto pr-2">
                  {result.nlp_analysis && result.nlp_analysis.length > 0 ? (
                    result.nlp_analysis.map((warn, i) => (
                      <div key={i} className={`p-4 rounded-2xl flex gap-4 items-start ${warn.item === 'Clean' ? 'bg-emerald-50/50' : 'bg-rose-50/50 border border-rose-100/50'}`}>
                        {warn.item === 'Clean' ? 
                          <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" /> : 
                          <AlertCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
                        }
                        <div>
                          <p className={`font-bold text-sm ${warn.item === 'Clean' ? 'text-emerald-800' : 'text-rose-800'}`}>{warn.item}</p>
                          <p className={`text-xs mt-1 leading-relaxed ${warn.item === 'Clean' ? 'text-emerald-600' : 'text-rose-600'}`}>{warn.reason}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-400 text-sm italic text-center py-10">No ingredient text provided for analysis.</div>
                  )}
                </div>
              </section>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

// Sub-component for Nutritional Progress Bars
function NutritionBar({ label, value, max, unit, icon, color, isWarning }) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  
  return (
    <div className="space-y-2 group">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2 text-slate-600 font-semibold text-sm">
          <span className={`text-slate-400 group-hover:${color.replace('bg-', 'text-')} transition-colors`}>{icon}</span>
          {label}
        </div>
        <div className="font-bold text-slate-900">
          {value.toFixed(1)}<span className="text-xs text-slate-400 ml-1 font-medium">{unit}</span>
        </div>
      </div>
      <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full transition-all duration-1000 ${isWarning ? 'bg-rose-500 animate-pulse' : color}`} 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
}
