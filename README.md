# DevStudio

An advanced AI-powered tool that enables developers to implement complex features and modify codebases using natural language instructions.

## Table of Contents
- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Description

DevStudio is a revolutionary tool designed for developers who want to leverage the power of AI in their coding workflow. It allows developers to describe desired changes or new features in natural language, and the AI generates the corresponding code, integrating seamlessly with existing codebases.

This tool bridges the gap between high-level concept expression and low-level code implementation, enabling developers to focus on problem-solving and design while the AI handles the intricacies of syntax and implementation details.

## Features

- **Natural Language Processing**: Interpret complex development instructions in plain English.
- **Contextual Code Generation**: Generate, modify, and refactor code based on the existing codebase and natural language prompts.
- **Intelligent Version Control Integration**: Automatic Git commit creation with descriptive messages.
- **Multi-Language Support**: Works with various programming languages and frameworks.
- **Smart Dependency Management**: Understands and suggests necessary dependencies for new features.
- **Code Explanation**: Provides detailed explanations of generated code .
- **Interactive Development**: Allows for iterative refinement of generated code through further prompts.

## Installation

```bash
# Clone the repository
git clone https://github.com/sekipaolo/devstudio.git

# Navigate to the project directory
cd devstudio

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configurations
```

## Usage

1. Start the AI Code Assistant:

```bash
python main.py /path/to/your/project
```

2. In the GUI, select the files relevant to your task.

3. Enter your prompt describing the changes or new feature you want to implement.

4. Review the AI-generated changes in the GUI.

5. Apply the changes if satisfied, or provide further instructions to refine the output.

## Examples

### Example 1: Adding Portfolio Composition Management

**User Prompt:**
```
The portfolio page should allow handling changes in the portfolio composition. 
Add routes for portfolio composition if necessary, or expand existing portfolio routes. 
For an asset in the portfolio, either weight or quantity can be set, and the other 
should be calculated. Either weight or quantity can be provided, with the rest calculated.
```

**AI-Generated Code:**
```python
@router.post("/{portfolio_id}/compositions")
def add_composition(portfolio_id: int, composition: schemas.PortfolioCompositionCreate, db: Session = Depends(get_db)):
    db_portfolio = db.query(models.Portfolio).filter(models.Portfolio.id == portfolio_id).first()
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    db_symbol = db.query(models.Symbol).filter(models.Symbol.symbol == composition.symbol).first()
    if db_symbol is None:
        raise HTTPException(status_code=404, detail="Symbol not found")
    
    total_invested = db_portfolio.total_invested()
    latest_price = db_symbol.daily_closes[-1].close if db_symbol.daily_closes else 0
    
    if composition.quantity is not None:
        weight = (composition.quantity * latest_price) / total_invested * 100 if total_invested > 0 else 0
    elif composition.weight is not None:
        quantity = (composition.weight / 100 * total_invested) / latest_price if latest_price > 0 else 0
    else:
        raise HTTPException(status_code=400, detail="Either quantity or weight must be provided")
    
    db_composition = models.PortfolioComposition(
        portfolio_id=portfolio_id,
        symbol_id=db_symbol.id,
        quantity=quantity,
        weight=weight
    )
    db.add(db_composition)
    db.commit()
    db.refresh(db_composition)
    return db_composition

# ... [Additional update and delete routes omitted for brevity]
```

This example demonstrates the AI's ability to:
- Understand complex financial concepts
- Implement new API routes with appropriate error handling
- Perform calculations based on user-provided data
- Integrate with existing database models and queries

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.