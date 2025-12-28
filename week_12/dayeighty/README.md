
# Day 80: Continuous Integration (CI/CD) Pipeline for Trading Systems

## Objective
Design and implement automated testing, validation, and deployment pipelines for trading systems, ensuring production readiness.

## Core Concepts
* CI/CD Architecture for Trading: Version control strategies for trading algorithms and configurations, automated testing suites for strategy validation, environment-specific configuration management
* Automated Validation Pipelines: Unit, integration, and system test automation, performance regression testing and alerting, risk limit validation and compliance checking
* Deployment Strategies: Blue-green deployments for trading systems, feature flag management for gradual rollouts, rollback procedures and emergency protocols
* Monitoring and Alerting: Performance degradation detection, risk limit breach alerts, system health monitoring and SLA tracking

## Tutorial: GitHub Actions Workflow for Trading Systems

This tutorial creates a comprehensive GitHub Actions workflow that automatically runs backtests, calculates performance metrics, generates reports on every commit, and implements risk validation checks.

```python
# .github/workflows/trading-ci.yml
name: Trading System CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # Daily backtest at market close (4 PM EST)
    - cron: '0 21 * * 1-5'

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install black flake8 mypy pytest pytest-cov
    
    - name: Code formatting check (Black)
      run: black --check .
    
    - name: Linting (Flake8)
      run: flake8 . --count --max-complexity=10 --statistics
    
    - name: Type checking (MyPy)
      run: mypy . --ignore-missing-imports
    
    - name: Run unit tests
      run: pytest tests/unit --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  backtest-validation:
    runs-on: ubuntu-latest
    needs: code-quality
    env:
      PYTHONPATH: ${{ github.workspace }}/src
      BACKTEST_DATA_PATH: ${{ github.workspace }}/data
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-backtest.txt
    
    - name: Download market data
      run: |
        python scripts/download_data.py \
          --start-date 2020-01-01 \
          --end-date $(date +%Y-%m-%d) \
          --symbols SPY QQQ IWM TLT \
          --output $BACKTEST_DATA_PATH/market_data.csv
    
    - name: Run backtest suite
      run: |
        python -m pytest tests/backtest \
          --tb=short \
          --junitxml=backtest-results.xml \
          --cov=src \
          --cov-report=xml
    
    - name: Generate backtest report
      run: |
        python scripts/generate_backtest_report.py \
          --input backtest-results.xml \
          --output backtest-report.html \
          --email-alert
    
    - name: Upload backtest results
      uses: actions/upload-artifact@v3
      with:
        name: backtest-report
        path: backtest-report.html
    
    - name: Slack notification on failure
      if: failure()
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#trading-alerts'
        username: 'CI/CD Bot'
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

  risk-validation:
    runs-on: ubuntu-latest
    needs: backtest-validation
    env:
      RISK_THRESHOLDS: '{"max_drawdown": 0.25, "var_95": 0.05, "concentration_limit": 0.15}'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install risk analysis dependencies
      run: |
        pip install riskfolio-lib pyportfolioopt cvxopt
    
    - name: Run risk validation
      run: |
        python scripts/validate_risk_limits.py \
          --backtest-results backtest-results.xml \
          --thresholds "$RISK_THRESHOLDS" \
          --output risk-validation.json
    
    - name: Check risk limits
      id: risk_check
      run: |
        python scripts/check_risk_compliance.py \
          --validation-file risk-validation.json \
          --fail-on-violation
    
    - name: Upload risk report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: risk-validation
        path: risk-validation.json

  performance-regression:
    runs-on: ubuntu-latest
    needs: risk-validation
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: pip install pandas numpy scipy matplotlib
    
    - name: Check performance regression
      run: |
        python scripts/check_performance_regression.py \
          --current backtest-results.xml \
          --baseline main \
          --threshold 0.1 \
          --metric sharpe
    
    - name: Generate performance comparison
      run: |
        python scripts/generate_performance_comparison.py \
          --current backtest-results.xml \
          --previous backtest-results-previous.xml \
          --output performance-delta.md

  deploy-staging:
    runs-on: ubuntu-latest
    needs: [performance-regression, risk-validation]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: staging
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: trading-system
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service \
          --cluster trading-cluster \
          --service trading-service \
          --force-new-deployment \
          --region us-east-1
    
    - name: Run staging tests
      run: |
        python scripts/run_staging_tests.py \
          --environment staging \
          --timeout 300

  paper-trading:
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: paper-trading
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy paper trading
      run: |
        python scripts/deploy_paper_trading.py \
          --image-tag ${{ github.sha }} \
          --duration 24h \
          --capital 100000
    
    - name: Monitor paper trading
      run: |
        python scripts/monitor_paper_trading.py \
          --check-interval 300 \
          --max-drawdown 0.05 \
          --alert-slack
    
    - name: Generate paper trading report
      if: always()
      run: |
        python scripts/generate_paper_report.py \
          --output paper-trading-report.md

  deploy-production:
    runs-on: ubuntu-latest
    needs: paper-trading
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Production validation gates
      run: |
        python scripts/validate_production_gates.py \
          --paper-results paper-trading-report.md \
          --risk-results risk-validation.json \
          --performance-results backtest-results.xml \
          --require-all-pass
    
    - name: Blue-green deployment
      run: |
        python scripts/blue_green_deployment.py \
          --current-green production-green \
          --new-blue production-blue-${{ github.sha }} \
          --validation-time 3600
    
    - name: Smoke tests
      run: |
        python scripts/run_smoke_tests.py \
          --environment production \
          --tests connectivity market-data order-execution
    
    - name: Rollback on failure
      if: failure()
      run: |
        python scripts/rollback_deployment.py \
          --previous-version production-green \
          --reason "CI/CD pipeline failure"
```

The CI/CD pipeline implements professional-grade validation including risk limit checks, performance regression testing, paper trading validation, and blue-green deployments with automatic rollback capabilities.

## Challenge: Complete CI/CD Pipeline with Production Deployment Gates

Implement a complete CI/CD pipeline with staging environments, automated paper trading, and production deployment gates with risk checks.

```python
class TradingSystemCIPipeline:
    """
    Complete CI/CD pipeline implementation for trading systems.
    """
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.environments = ['development', 'staging', 'paper', 'production']
        self.deployment_gates = {}
        
    def run_full_pipeline(self, commit_sha: str, branch: str):
        """
        Execute complete CI/CD pipeline.
        
        Parameters:
        -----------
        commit_sha : str
            Git commit SHA being deployed
        branch : str
            Source branch
        """
        pipeline_start = datetime.now()
        pipeline_results = {
            'commit_sha': commit_sha,
            'branch': branch,
            'start_time': pipeline_start,
            'stages': {}
        }
        
        try:
            # Stage 1: Code quality and testing
            print("Stage 1: Code Quality and Testing")
            test_results = self._run_test_stage()
            pipeline_results['stages']['testing'] = test_results
            
            if not test_results['passed']:
                raise PipelineError("Testing stage failed")
            
            # Stage 2: Backtest validation
            print("Stage 2: Backtest Validation")
            backtest_results = self._run_backtest_stage()
            pipeline_results['stages']['backtesting'] = backtest_results
            
            # Stage 3: Risk validation
            print("Stage 3: Risk Validation")
            risk_results = self._run_risk_validation(backtest_results)
            pipeline_results['stages']['risk_validation'] = risk_results
            
            if not risk_results['passed']:
                raise PipelineError("Risk validation failed")
            
            # Stage 4: Staging deployment
            print("Stage 4: Staging Deployment")
            staging_results = self._deploy_to_staging(commit_sha)
            pipeline_results['stages']['staging'] = staging_results
            
            # Stage 5: Paper trading
            print("Stage 5: Paper Trading")
            paper_results = self._run_paper_trading(commit_sha)
            pipeline_results['stages']['paper_trading'] = paper_results
            
            # Stage 6: Production gates
            print("Stage 6: Production Deployment Gates")
            gate_results = self._check_production_gates(
                test_results, backtest_results, risk_results, paper_results
            )
            pipeline_results['stages']['production_gates'] = gate_results
            
            if not gate_results['passed']:
                raise PipelineError("Production gates failed")
            
            # Stage 7: Production deployment
            print("Stage 7: Production Deployment")
            production_results = self._deploy_to_production(commit_sha)
            pipeline_results['stages']['production'] = production_results
            
            pipeline_results['status'] = 'success'
            pipeline_results['end_time'] = datetime.now()
            
        except PipelineError as e:
            pipeline_results['status'] = 'failed'
            pipeline_results['error'] = str(e)
            pipeline_results['end_time'] = datetime.now()
            
            # Trigger rollback if needed
            self._trigger_rollback(commit_sha)
            
            # Send alert
            self._send_alert(f"Pipeline failed: {str(e)}")
        
        return pipeline_results
    
    def _run_test_stage(self) -> Dict:
        """Run comprehensive test suite."""
        results = {
            'unit_tests': self._run_unit_tests(),
            'integration_tests': self._run_integration_tests(),
            'performance_tests': self._run_performance_tests(),
            'security_tests': self._run_security_tests()
        }
        
        # Calculate overall pass/fail
        all_passed = all(r['passed'] for r in results.values())
        results['passed'] = all_passed
        
        return results
    
    def _run_backtest_stage(self) -> Dict:
        """Run backtest validation."""
        backtest_config = {
            'start_date': '2020-01-01',
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'initial_capital': 100000,
            'commission': 0.001,
            'slippage': 0.0005
        }
        
        # Run backtest on multiple time periods
        periods = [
            ('2020-01-01', '2021-12-31'),  # Training
            ('2022-01-01', '2022-12-31'),  # Validation
            ('2023-01-01', '2023-12-31')   # Testing
        ]
        
        period_results = {}
        for i, (start, end) in enumerate(periods):
            period_name = f'period_{i+1}'
            period_results[period_name] = self._run_single_backtest(start, end)
        
        # Calculate consistency metrics
        consistency = self._calculate_backtest_consistency(period_results)
        
        return {
            'period_results': period_results,
            'consistency_metrics': consistency,
            'passed': consistency['score'] >= 0.7  # 70% consistency threshold
        }
    
    def _run_risk_validation(self, backtest_results: Dict) -> Dict:
        """Validate risk limits and compliance."""
        risk_limits = self.config['risk_limits']
        violations = []
        
        for period_name, period_result in backtest_results['period_results'].items():
            # Check maximum drawdown
            if period_result['max_drawdown'] > risk_limits['max_drawdown']:
                violations.append({
                    'period': period_name,
                    'metric': 'max_drawdown',
                    'value': period_result['max_drawdown'],
                    'limit': risk_limits['max_drawdown']
                })
            
            # Check Value at Risk
            if period_result['var_95'] > risk_limits['var_95']:
                violations.append({
                    'period': period_name,
                    'metric': 'var_95',
                    'value': period_result['var_95'],
                    'limit': risk_limits['var_95']
                })
            
            # Check concentration limits
            for symbol, concentration in period_result['concentration'].items():
                if concentration > risk_limits['concentration_limit']:
                    violations.append({
                        'period': period_name,
                        'metric': f'concentration_{symbol}',
                        'value': concentration,
                        'limit': risk_limits['concentration_limit']
                    })
        
        return {
            'violations': violations,
            'passed': len(violations) == 0,
            'risk_score': self._calculate_risk_score(backtest_results)
        }
    
    def _run_paper_trading(self, commit_sha: str) -> Dict:
        """Run automated paper trading validation."""
        paper_config = {
            'duration_hours': 24,
            'initial_capital': 100000,
            'max_positions': 10,
            'risk_per_trade': 0.02
        }
        
        # Deploy paper trading environment
        deployment_id = self._deploy_paper_environment(commit_sha, paper_config)
        
        # Monitor paper trading
        monitor_results = self._monitor_paper_trading(deployment_id, paper_config['duration_hours'])
        
        # Analyze results
        analysis = self._analyze_paper_results(monitor_results)
        
        # Clean up paper environment
        self._cleanup_paper_environment(deployment_id)
        
        return {
            'deployment_id': deployment_id,
            'monitor_results': monitor_results,
            'analysis': analysis,
            'passed': analysis['overall_score'] >= 0.8  # 80% success threshold
        }
    
    def _check_production_gates(self, *stage_results) -> Dict:
        """Check all production deployment gates."""
        gates = [
            self._check_test_coverage_gate(stage_results[0]),
            self._check_performance_gate(stage_results[1]),
            self._check_risk_gate(stage_results[2]),
            self._check_paper_trading_gate(stage_results[3]),
            self._check_business_hours_gate(),
            self._check_team_approval_gate()
        ]
        
        passed_gates = [g for g in gates if g['passed']]
        
        return {
            'gates': gates,
            'passed_gates': len(passed_gates),
            'total_gates': len(gates),
            'passed': len(passed_gates) == len(gates)
        }
    
    def _check_test_coverage_gate(self, test_results: Dict) -> Dict:
        """Check test coverage requirements."""
        coverage = test_results.get('coverage', {})
        required_coverage = self.config['test_coverage_requirements']
        
        checks = []
        for metric, required in required_coverage.items():
            actual = coverage.get(metric, 0)
            passed = actual >= required
            checks.append({
                'metric': metric,
                'actual': actual,
                'required': required,
                'passed': passed
            })
        
        all_passed = all(c['passed'] for c in checks)
        
        return {
            'name': 'test_coverage',
            'checks': checks,
            'passed': all_passed
        }
    
    def _check_performance_gate(self, backtest_results: Dict) -> Dict:
        """Check performance consistency requirements."""
        consistency = backtest_results['consistency_metrics']
        requirements = self.config['performance_requirements']
        
        checks = []
        for metric, required in requirements.items():
            actual = consistency.get(metric, 0)
            passed = actual >= required
            checks.append({
                'metric': metric,
                'actual': actual,
                'required': required,
                'passed': passed
            })
        
        all_passed = all(c['passed'] for c in checks)
        
        return {
            'name': 'performance_consistency',
            'checks': checks,
            'passed': all_passed
        }
    
    def _check_risk_gate(self, risk_results: Dict) -> Dict:
        """Check risk limit requirements."""
        violations = risk_results['violations']
        risk_score = risk_results['risk_score']
        
        passed = len(violations) == 0 and risk_score >= self.config['minimum_risk_score']
        
        return {
            'name': 'risk_limits',
            'violation_count': len(violations),
            'risk_score': risk_score,
            'minimum_score': self.config['minimum_risk_score'],
            'passed': passed
        }
    
    def _check_paper_trading_gate(self, paper_results: Dict) -> Dict:
        """Check paper trading results."""
        analysis = paper_results['analysis']
        requirements = self.config['paper_trading_requirements']
        
        checks = []
        for metric, required in requirements.items():
            actual = analysis.get(metric, 0)
            passed = actual >= required
            checks.append({
                'metric': metric,
                'actual': actual,
                'required': required,
                'passed': passed
            })
        
        all_passed = all(c['passed'] for c in checks)
        
        return {
            'name': 'paper_trading',
            'checks': checks,
            'passed': all_passed
        }
    
    def _check_business_hours_gate(self) -> Dict:
        """Check if deployment is allowed during business hours."""
        now = datetime.now()
        current_hour = now.hour
        
        # Allow deployments only outside market hours (9:30 AM - 4:00 PM EST)
        # Convert to UTC (EST is UTC-5)
        market_open_utc = 14  # 9:30 AM EST = 14:30 UTC
        market_close_utc = 21  # 4:00 PM EST = 21:00 UTC
        
        # Check if current time is within market hours
        within_market_hours = market_open_utc <= current_hour < market_close_utc
        
        return {
            'name': 'business_hours',
            'current_time': now,
            'within_market_hours': within_market_hours,
            'passed': not within_market_hours
        }
    
    def _check_team_approval_gate(self) -> Dict:
        """Check if team approval is required and obtained."""
        if not self.config.get('require_team_approval', False):
            # Approval not required
            return {
                'name': 'team_approval',
                'required': False,
                'passed': True
            }
        
        # Check if approval was given
        # In practice, this would check a database or approval system
        approval_given = self._check_approval_system()
        
        return {
            'name': 'team_approval',
            'required': True,
            'approval_given': approval_given,
            'passed': approval_given
        }
    
    def _deploy_to_production(self, commit_sha: str) -> Dict:
        """Deploy to production using blue-green deployment."""
        deployment_strategy = self.config['deployment_strategy']
        
        if deployment_strategy == 'blue_green':
            return self._blue_green_deployment(commit_sha)
        elif deployment_strategy == 'canary':
            return self._canary_deployment(commit_sha)
        else:
            return self._standard_deployment(commit_sha)
    
    def _blue_green_deployment(self, commit_sha: str) -> Dict:
        """Implement blue-green deployment strategy."""
        # Get current active environment (blue or green)
        current_active = self._get_active_environment()
        new_environment = 'green' if current_active == 'blue' else 'blue'
        
        print(f"Current active: {current_active}, deploying to: {new_environment}")
        
        # Deploy to new environment
        deploy_result = self._deploy_to_environment(new_environment, commit_sha)
        
        if not deploy_result['success']:
            return {
                'strategy': 'blue_green',
                'success': False,
                'error': deploy_result['error']
            }
        
        # Run smoke tests on new environment
        smoke_tests = self._run_smoke_tests(new_environment)
        
        if not smoke_tests['passed']:
            # Rollback new environment
            self._rollback_environment(new_environment)
            return {
                'strategy': 'blue_green',
                'success': False,
                'error': 'Smoke tests failed'
            }
        
        # Switch traffic to new environment
        switch_result = self._switch_traffic(new_environment)
        
        if not switch_result['success']:
            # Rollback traffic switch
            self._switch_traffic(current_active)
            self._rollback_environment(new_environment)
            return {
                'strategy': 'blue_green',
                'success': False,
                'error': 'Traffic switch failed'
            }
        
        # Monitor new environment
        monitor_result = self._monitor_environment(new_environment, duration_minutes=60)
        
        if not monitor_result['healthy']:
            # Rollback to previous environment
            self._switch_traffic(current_active)
            self._rollback_environment(new_environment)
            return {
                'strategy': 'blue_green',
                'success': False,
                'error': 'Monitoring failed'
            }
        
        # Clean up old environment
        self._cleanup_environment(current_active)
        
        return {
            'strategy': 'blue_green',
            'success': True,
            'old_environment': current_active,
            'new_environment': new_environment,
            'switch_time': datetime.now()
        }
    
    def _trigger_rollback(self, commit_sha: str):
        """Trigger rollback to previous stable version."""
        print(f"Triggering rollback for commit {commit_sha}")
        
        # Get previous stable version
        previous_version = self._get_previous_stable_version()
        
        if previous_version:
            # Deploy previous version
            self._deploy_to_production(previous_version['commit_sha'])
            
            # Send rollback notification
            self._send_alert(
                f"Rollback triggered for commit {commit_sha}. "
                f"Reverted to {previous_version['commit_sha']}"
            )
        else:
            # No previous version, send alert
            self._send_alert(
                f"Rollback needed for commit {commit_sha} but no previous version found"
            )

# Next steps for the challenge:
# 1. Implement canary deployment strategy with gradual traffic shifting
# 2. Add feature flag management for controlled feature rollouts
# 3. Implement circuit breakers for automatic rollback on performance degradation
# 4. Add compliance checks for regulatory requirements
# 5. Implement disaster recovery procedures and backup validation
# 6. Create dashboard for pipeline monitoring and alerting
# 7. Add cost optimization checks for resource utilization
```

The challenge implements a complete CI/CD pipeline with production deployment gates, risk validation, paper trading environments, and sophisticated deployment strategies including blue-green deployments with automatic rollback capabilities.
```
