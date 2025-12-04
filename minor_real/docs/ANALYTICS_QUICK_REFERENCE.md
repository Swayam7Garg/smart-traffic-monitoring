# Analytics Dashboard - Quick Reference Card

## 🎯 Three View Modes

| Mode | Use When | Best For |
|------|----------|----------|
| **All Locations** | Start of shift / Overview | City-wide management |
| **By Location** | Analyzing specific junction | Signal timing optimization |
| **Last Video** | Just uploaded footage | Quick verification |

---

## 🚦 Smart Recommendations

| Alert | Congestion | What to Do |
|-------|------------|------------|
| 🚨 **Emergency Priority** | N/A | Extend green for emergency vehicles |
| 🔴 **High Congestion** | > 70% | Increase signal timing / Alternative routes |
| 🟡 **Moderate Traffic** | 30-70% | Monitor, no immediate action |
| 🟢 **Smooth Flow** | < 30% | Maintain current settings |

---

## 📊 Key Statistics

- **Total Vehicles**: Traffic volume (higher = busier)
- **Videos Analyzed**: Data reliability (more = better)
- **Avg per Video**: Traffic intensity (compare locations)
- **Avg Congestion**: 0-30% Low, 30-60% Moderate, 60%+ High
- **Emergency Alerts**: Requires immediate attention

---

## 🛠️ Common Actions

### View Overall Traffic
1. Click "All Locations"
2. Check recommendation at top
3. Review location comparison table

### Analyze Specific Junction
1. Click "By Location"
2. Select junction from dropdown
3. Set date range
4. Review peak hours chart

### Check Latest Upload
1. Click "Last Video"
2. Review vehicle count & congestion
3. Read recommendation
4. Download processed video

### Export Data
1. Set date range
2. Click "Export CSV"
3. Open in Excel

### Clear Test Data
1. Click "Clear Data" (red button)
2. Choose location or all
3. Confirm deletion

---

## ⚡ Quick Tips

✅ Start each shift with "All Locations" view
✅ Use "Last Video" after uploads for verification
✅ Export CSV monthly for records
✅ Clear test uploads immediately
✅ Act on recommendations, don't just read data

---

## 🎯 When to Adjust Signals

**Increase Green Time If**:
- Congestion > 60% consistently
- Peak hours chart shows red bars
- Emergency vehicles frequent
- Recommendation says "extend signal timing"

**Maintain Current If**:
- Congestion < 30%
- Recommendation says "smooth flow"
- No complaints from traffic officers

---

## 📍 Multi-Location Strategy

| Location | Avg Congestion | Action |
|----------|----------------|--------|
| High traffic (>60%) | Deploy officers / Adjust signals |
| Moderate (30-60%) | Monitor closely |
| Low (<30%) | No action needed |

**Priority**: Focus resources on highest congestion first!

---

## 🔄 Weekly Routine

**Monday**: Review last week's data → Adjust signal timing
**Daily**: Check "All Locations" at shift start
**After uploads**: Verify with "Last Video"
**Monthly**: Export CSV → Archive data → Clear test data

---

## ⚠️ Important Notes

- **Date range**: Default is last 7 days (update for today's data)
- **Emergency detection**: May have false positives (verify in video)
- **Clear history**: Cannot be undone! Confirm before deleting
- **Location dropdown**: Auto-populated from your uploads

---

## 📱 Server URLs

- **Frontend**: http://localhost:5176
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

**Remember**: Data without action is useless. Use recommendations to improve traffic flow! 🚦
