# Question Improvement Pipeline Web Application

A Flask-based web application that provides a complete question improvement pipeline with template matching, metrics calculation, and AI polishing capabilities.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/question-improvement-pipeline.git
   cd question-improvement-pipeline
   ```

2. **Download the data file**
   The `questions.csv` file (741MB) is too large for GitHub. You need to download it separately:
   
   **Option A: Download from Google Drive**
   - [Download questions.csv](https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=sharing)
   - Place it in the project root directory
   
   **Option B: Create a sample file**
   ```bash
   # Create a small sample for testing
   echo "id,text,lexical_path,type,error_traceback,choices" > questions.csv
   echo "1,Please provide username,user input,ValueNotKnownQuestion,,," >> questions.csv
   echo "2,Select one option,multiple choice,ValueNotKnownQuestion,,," >> questions.csv
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Install Ollama for AI polishing**
   - Download from https://ollama.ai
   - Install and start: `ollama serve`
   - Pull a model: `ollama pull llama2`

### Running the Application

1. **Run the setup script (optional but recommended)**
   ```bash
   python setup.py
   ```

2. **Start the Flask server**
   ```bash
   python app.py
   ```

3. **Open your browser**
   Navigate to: `http://localhost:5001`

## 📊 Features

### Web Interface Pages

- **Home** (`/`) - Navigation hub
- **Metrics Analysis** (`/metrics`) - Analyze any text for quality metrics
- **Question Improvement** (`/improve`) - Improve questions with templates and AI
- **Templates Browser** (`/templates`) - View all available prompt templates
- **Pipeline Diagram** (`/pipeline`) - Visual workflow explanation
- **Demo** (`/demo`) - Live examples from the dataset

### API Endpoints

- `POST /api/calculate_metrics` - Calculate metrics for any text
- `POST /api/improve_question` - Process questions through the pipeline
- `POST /api/start_ollama` - Manually trigger AI polishing
- `GET /api/demo_examples` - Get demo examples from CSV

## 🔧 How It Works

### 1. Template Matching
- Questions are matched against predefined templates using flexible regex
- Supports placeholders like `<FIELD>`, `<NUMBER>`, `<EXPRESSION>`
- Handles whitespace and punctuation variations

### 2. Metrics Calculation
- **Clarity**: How easy the text is to understand
- **Conciseness**: How brief and to-the-point the text is
- **Technical Accuracy**: How technically correct the content is
- **Actionability**: How actionable the instructions are

### 3. AI Polishing (Optional)
- Uses Ollama for additional improvement
- Only triggers when enhanced score < 9.0
- Provides fallback when Ollama is unavailable

## 📁 File Structure

### Core Application Files
```
app.py                          # Flask web server
simple_question_tester.py       # Question processing engine
metrics3.py                     # Quality metrics calculation
local_polisher.py              # AI polishing with Ollama
```

### Templates (HTML)
```
templates/
├── index.html                  # Home page
├── metrics.html               # Metrics analysis page
├── improve.html               # Question improvement page
├── templates.html             # Template browser
├── pipeline.html              # Workflow diagram
└── demo.html                  # Live demo page
```

### Data
```
questions.csv                   # Main dataset (741MB) - Download separately
```

## 🛠️ Configuration

### Port Configuration
The app runs on port 5001 by default. If you need to change it:
```python
# In app.py, line 354
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Ollama Configuration
To enable AI polishing:
1. Install Ollama: https://ollama.ai
2. Start the service: `ollama serve`
3. Pull a model: `ollama pull llama2`

The app will work without Ollama, but AI polishing features will be disabled.

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in `app.py` line 354
   - Or kill the process using the port

2. **Missing dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Missing questions.csv file**
   - Download the file from the provided link
   - Or create a sample file as shown in the installation instructions

4. **Ollama not available**
   - The app works without Ollama
   - AI polishing features will be disabled
   - Check `local_polisher.py` for Ollama setup

5. **Large CSV file loading slowly**
   - The 741MB `questions.csv` file may take time to load
   - Consider using a smaller sample for testing

### Debug Mode
The app runs in debug mode by default, which provides:
- Auto-reload on file changes
- Detailed error messages
- Debug PIN for accessing debugger

## 📈 Performance

- **Startup time**: ~30 seconds (loading 4M+ questions from CSV)
- **Memory usage**: ~2GB RAM (with full dataset)
- **Response time**: <1 second for most operations

## 🔒 Security Notes

- Debug mode is enabled (not recommended for production)
- No authentication implemented
- Runs on all interfaces (0.0.0.0)

## 📝 Development

### Adding New Templates
Edit `simple_question_tester.py` and add to the `PROMPT_TEMPLATES` dictionary.

### Modifying Metrics
Edit `metrics3.py` to adjust the quality calculation algorithms.

### Customizing the UI
Modify files in the `templates/` directory to change the web interface.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and research purposes.

---

**Note**: The `questions.csv` file (741MB) is not included in this repository due to GitHub's file size limits. Please download it separately or create a sample file for testing. 