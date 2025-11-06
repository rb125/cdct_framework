# CDCT Model Ranking Web Application

A modern, responsive web application for visualizing and comparing language model performance based on the CDCT (Compression-Decay Comprehension Test) framework.

## Features

### 🏆 Overall Rankings
- Interactive leaderboard with sortable columns
- Support for multiple ranking metrics (CSI, C_h, Mean Score)
- Real-time filtering and sorting
- Visual indicators for top performers

### 📊 Domain-Specific Analysis
- Browse rankings by domain (Mathematics, Physics, Biology, etc.)
- Compare model performance across different knowledge areas
- Detailed domain-specific statistics

### 🔍 Model Comparison
- Side-by-side comparison of multiple models
- Statistical analysis across all experiments
- Performance trends and insights

### 📈 Interactive Visualizations
- Bar charts for CSI and performance scores
- Built with Chart.js for smooth, responsive graphics
- Automatic updates when data changes

## Architecture

```
web_ranking/
├── api/                      # FastAPI Backend
│   ├── __init__.py
│   ├── main.py              # FastAPI application & routes
│   ├── models.py            # Pydantic schemas
│   └── data_processor.py    # Data processing logic
├── static/                   # Frontend
│   └── index.html           # Single-page application
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- CDCT framework results (consolidated_results.json)

### Step 1: Install Dependencies

```bash
cd web_ranking
pip install -r requirements.txt
```

### Step 2: Verify Data Files

Ensure the following files exist in the parent directory:
- `../consolidated_results.json` - Consolidated experimental results
- `../results/` - Directory with individual result files

If these don't exist, run the CDCT framework experiments first:
```bash
cd ..
python run_all.py
python consolidate_result.py
```

## Running the Application

### Development Mode

```bash
# From the web_ranking directory
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the Python entry point:
```bash
python -c "from api.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

### Production Mode

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The application will be available at:
- **Frontend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Alternative API Docs**: http://localhost:8000/api/redoc

## API Endpoints

### Health & Info
- `GET /api/health` - Health check
- `GET /api/stats/summary` - Overall summary statistics

### Rankings
- `GET /api/rankings` - Overall model rankings
  - Query params: `sort_by` (CSI|C_h|mean_score), `ascending` (true|false)
- `GET /api/domains` - List all domains
- `GET /api/domains/{domain}/rankings` - Domain-specific rankings
- `GET /api/models` - List all models
- `GET /api/models/{model_name}` - Detailed model statistics

### Comparison & Performance
- `GET /api/compare?models={model1}&models={model2}` - Compare models
- `GET /api/performance/{model_name}/{concept}` - Performance data

## Usage Examples

### View Rankings

1. Open http://localhost:8000 in your browser
2. Use the "Sort by" dropdown to change ranking metric
3. Click column headers to sort (if table sorting is enabled)
4. View top 3 models highlighted in gold, silver, bronze

### Compare Models

1. Click the "Compare Models" tab
2. Select 2 or more models using checkboxes
3. Click "Compare Selected"
4. View side-by-side statistics

### Explore Domains

1. Click the "By Domain" tab
2. Browse domain cards showing best performers
3. Click any domain card for detailed rankings
4. View concept-specific performance

### Visualizations

1. Click the "Visualizations" tab
2. View CSI comparison chart (lower is better)
3. View Mean Score comparison chart (higher is better)
4. Charts update automatically when rankings change

## API Usage (cURL Examples)

```bash
# Get overall rankings
curl http://localhost:8000/api/rankings

# Get rankings sorted by mean score (descending)
curl "http://localhost:8000/api/rankings?sort_by=mean_score&ascending=false"

# Get mathematics domain rankings
curl http://localhost:8000/api/domains/mathematics/rankings

# Get model details
curl http://localhost:8000/api/models/gpt-5-mini

# Compare two models
curl "http://localhost:8000/api/compare?models=gpt-5-mini&models=deepseek-v3-0324"

# Get performance data
curl http://localhost:8000/api/performance/gpt-5-mini/derivative
```

## Understanding the Metrics

### CSI (Compression Stability Index)
- **Lower is better** (indicates more stable comprehension)
- Measures the rate of performance decay as information is compressed
- Best models: 0.08-0.12
- Poor models: >0.19

### C_h (Comprehension Horizon)
- **Lower is better** (indicates less information needed)
- Minimum compression fraction where model achieves 70% performance
- Shows how resilient model comprehension is under information constraints

### Mean Score
- **Higher is better** (0-1 scale)
- Average performance across all compression levels
- Combines keyword matching, hallucination detection, and response quality

### R² (Goodness of Fit)
- Measures linearity of decay pattern
- >0.5 is good (linear decay = true comprehension)
- <0.3 warns of non-linear patterns (possible memorization)

## Development

### Adding New Features

1. **Backend (API)**: Edit `api/main.py` to add new endpoints
2. **Data Processing**: Modify `api/data_processor.py` for new data transformations
3. **Frontend**: Update `static/index.html` for UI changes

### Testing

```bash
# Test API endpoint
curl http://localhost:8000/api/health

# Test with browser DevTools
# Open http://localhost:8000
# Check Console for errors
# Inspect Network tab for API calls
```

### CORS Configuration

For production, update CORS settings in `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["GET"],  # Limit to needed methods
    allow_headers=["*"],
)
```

## Troubleshooting

### Issue: "consolidated_results.json not found"
**Solution**: Run `python consolidate_result.py` from the parent directory

### Issue: "No data available"
**Solution**: Ensure CDCT experiments have been run (`python run_all.py`)

### Issue: Port 8000 already in use
**Solution**: Use a different port:
```bash
uvicorn api.main:app --port 8001
```

### Issue: CORS errors in browser
**Solution**: Ensure CORS middleware is enabled in `api/main.py`

### Issue: Charts not displaying
**Solution**: Check browser console for Chart.js loading errors. Ensure internet connection for CDN.

## Performance Optimization

For large datasets:
1. Enable caching in `data_processor.py`
2. Use database instead of JSON files
3. Implement pagination for large result sets
4. Add Redis for caching API responses

## Security Considerations

- **Input Validation**: All inputs validated via Pydantic models
- **CORS**: Configure allowed origins for production
- **Rate Limiting**: Consider adding rate limiting for public deployments
- **Authentication**: Add auth middleware for private deployments

## Future Enhancements

- [ ] Database backend (PostgreSQL/SQLite)
- [ ] Real-time updates via WebSockets
- [ ] Export rankings to CSV/PDF
- [ ] User authentication and saved comparisons
- [ ] Advanced filtering (by date, strategy, evaluation mode)
- [ ] Performance trend analysis over time
- [ ] Integration with model hosting platforms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Part of the CDCT Framework - see parent directory for license information.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review API documentation at http://localhost:8000/api/docs
3. Check parent CDCT framework documentation
4. Review console logs for error messages

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Chart.js](https://www.chartjs.org/) - JavaScript charting library
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

Developed for the CDCT (Compression-Decay Comprehension Test) Framework.
