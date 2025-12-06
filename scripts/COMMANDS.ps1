#!/usr/bin/env pwsh
# Quick Commands Reference for Chit Fund Manager

Write-Host "🎯 Chit Fund Manager - Quick Commands" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 Setup (First Time)" -ForegroundColor Yellow
Write-Host "  uv sync                    # Install dependencies"
Write-Host "  uv sync --extra e2e        # Install with E2E testing"
Write-Host ""

Write-Host "🚀 Run Application" -ForegroundColor Green
Write-Host "  uv run python -m streamlit run streamlit_app/main.py --server.port 8501"
Write-Host "  OR"
Write-Host "  uv run python run_app.py"
Write-Host ""

Write-Host "🧪 Testing" -ForegroundColor Magenta
Write-Host "  uv run playwright install chromium    # First time only"
Write-Host "  uv run pytest tests/e2e/ -v          # Run all E2E tests"
Write-Host "  uv run pytest tests/e2e/test_user_flow.py::test_login_flow -v"
Write-Host ""

Write-Host "📊 Access Points" -ForegroundColor Blue
Write-Host "  App URL: http://localhost:8501"
Write-Host "  Database: data/chit_fund_db.xlsx"
Write-Host ""

Write-Host "📝 Documentation" -ForegroundColor White
Write-Host "  TESTING_GUIDE.md           # Complete testing guide"
Write-Host "  DEPLOYMENT_COMPLETE.md     # Deployment summary"
Write-Host "  streamlit_app/README.md    # Quick reference"
Write-Host ""

Write-Host "✨ Status: Application is READY!" -ForegroundColor Green
Write-Host ""
