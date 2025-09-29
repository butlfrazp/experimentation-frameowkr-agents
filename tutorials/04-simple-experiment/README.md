# 🏗️ Build a Simple Experiment

Learn to create experiments from scratch with step-by-step guidance.

## 🎯 What You'll Build

A **text summarization** experiment that:
- Takes long articles as input
- Generates summaries using different approaches
- Evaluates summary quality and relevance

## Step 1: Create the Module

First, let's create a simple summarization module:

```python
# summarizer.py
def run(input_data: str, max_length: int = 100) -> str:
    """
    Simple text summarization using sentence extraction.
    """
    sentences = input_data.split('.')
    
    # Simple heuristic: take first few sentences
    summary_sentences = sentences[:2]
    
    summary = '. '.join(summary_sentences).strip()
    
    # Ensure it ends properly
    if summary and not summary.endswith('.'):
        summary += '.'
    
    return summary
```

## Step 2: Prepare Your Dataset

Create test data for summarization:

```yaml
# flow.flex.yaml
dataset:
  type: inline
  data:
    - input: "Artificial intelligence is transforming industries worldwide. Companies are investing billions in AI research and development. Machine learning algorithms are becoming more sophisticated every year. The future of AI looks incredibly promising with new breakthroughs happening regularly."
      expected_output: "Artificial intelligence is transforming industries worldwide. Companies are investing billions in AI research and development."
      context: "ai_overview"
      
    - input: "Climate change is one of the most pressing issues of our time. Rising temperatures are causing ice caps to melt at an alarming rate. Scientists are working on innovative solutions to reduce carbon emissions. Renewable energy sources are becoming more cost-effective and efficient."
      expected_output: "Climate change is one of the most pressing issues of our time. Rising temperatures are causing ice caps to melt at an alarming rate."
      context: "climate_change"
```

## Step 3: Configure Evaluation

Set up evaluators to measure performance:

```yaml
evaluators:
  - name: response_relevance
    type: platform
    config:
      include_reasoning: true
      
  - name: conversation_quality  
    type: platform
    config:
      min_score_threshold: 0.6
```

## Step 4: Complete Configuration

Put it all together:

```yaml
name: simple_summarization_experiment
description: "Learn to build experiments: Text summarization with quality evaluation"

dataset:
  type: inline
  data:
    - input: "Artificial intelligence is transforming industries worldwide. Companies are investing billions in AI research and development. Machine learning algorithms are becoming more sophisticated every year. The future of AI looks incredibly promising with new breakthroughs happening regularly."
      expected_output: "Artificial intelligence is transforming industries worldwide. Companies are investing billions in AI research and development."
      context: "ai_overview"
      
    - input: "Climate change is one of the most pressing issues of our time. Rising temperatures are causing ice caps to melt at an alarming rate. Scientists are working on innovative solutions to reduce carbon emissions. Renewable energy sources are becoming more cost-effective and efficient."
      expected_output: "Climate change is one of the most pressing issues of our time. Rising temperatures are causing ice caps to melt at an alarming rate."
      context: "climate_change"

evaluators:
  - name: response_relevance
    type: platform
    config:
      include_reasoning: true
      
  - name: conversation_quality
    type: platform  
    config:
      min_score_threshold: 0.6

execution:
  module: "summarizer"
  parallel: false
  timeout: 30
  
output:
  save_individual_results: true
  include_metadata: true
  format: "json"
```

## Step 5: Run Your Experiment

```bash
# From this tutorial directory
exp-cli run flow.flex.yaml

# Or run the entire directory
exp-cli run-directory . --install-deps
```

## Step 6: Analyze Results

Your results will be saved in `data/experiments/`. Look for:

### Results Overview
```json
{
  "experiment_name": "simple_summarization_experiment",
  "total_samples": 2,
  "evaluator_results": {
    "response_relevance": {
      "average_score": 0.85,
      "individual_scores": [0.9, 0.8]
    },
    "conversation_quality": {
      "average_score": 0.75,
      "passed_threshold": true
    }
  }
}
```

## 🎨 Customization Ideas

Try these modifications to learn more:

### Improve the Summarizer
```python
def run(input_data: str, max_length: int = 100) -> str:
    sentences = input_data.split('.')
    
    # Score sentences by position and length
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            # Earlier sentences and longer sentences score higher
            score = (len(sentences) - i) * len(sentence.strip())
            scored_sentences.append((score, sentence.strip()))
    
    # Take top 2 sentences
    scored_sentences.sort(reverse=True)
    summary_sentences = [s[1] for s in scored_sentences[:2]]
    
    return '. '.join(summary_sentences) + '.'
```

### Add More Evaluators
```yaml
evaluators:
  - name: response_relevance
    type: platform
    config:
      include_reasoning: true
      
  - name: conversation_quality
    type: platform
    config:
      min_score_threshold: 0.6
      
  # Add custom evaluation criteria
  - name: custom_length_check
    type: foundry
    config:
      evaluator_file: "length_evaluator.py"
```

### Expand the Dataset
```yaml
dataset:
  type: file
  path: "articles.csv"  # Load from CSV file
  columns:
    input: "article_text"
    expected_output: "human_summary"
    context: "topic"
```

## 🔍 Understanding the Results

### Key Metrics to Watch
- **Response Relevance**: How well does the summary match the expected output?
- **Conversation Quality**: Overall quality of the generated text
- **Execution Time**: How long did processing take?

### Improving Performance
- **Low Relevance**: Adjust summarization algorithm
- **Quality Issues**: Improve text generation logic  
- **Slow Execution**: Optimize processing or enable parallel execution

## 🚀 Next Steps

- **[Configuration Deep Dive](../05-configuration/)** - Master YAML configuration
- **[Evaluator Guide](../06-evaluators/)** - Understand evaluation metrics
- **[Foundry Evaluators](../07-foundry-evaluators/)** - Create custom evaluators

---

**🎉 Great Job!** You've built a complete experiment from scratch. This pattern works for any evaluation scenario!