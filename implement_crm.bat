@echo off
echo ========================================
echo CRM Implementation with Claude Code
echo ========================================
echo.
echo This will implement the Pipedrive-inspired CRM system
echo using the generated design documents.
echo.

cd /d "d:\Repository\@Clients\FY.WB.Midway"

echo Starting Claude Code implementation...
echo.

wsl -d Ubuntu -e bash -c "cd /mnt/d/Repository/@Clients/FY.WB.Midway && claude --add-dir generated_documents/design --add-dir Requirements_Artifacts -p 'Implement the complete CRM system based on the design documents. Focus on: 1) Backend API endpoints for pipeline management, deal cards, lead inbox, and activity scheduling. 2) Frontend React components for broker dashboard with kanban pipeline board, deal cards with drag-and-drop, lead inbox, and activity scheduler. 3) Database entities and migrations for deals, leads, activities, and pipeline stages. 4) Role-based access control for Broker vs Manager permissions. 5) Integration with existing authentication system. Use the exact specifications from CRM_Backend_Design.md and CRM_Frontend_Design.md. Implement all FR-01 to FR-10 functional requirements with full fidelity to the Pipedrive-inspired design.'"

echo.
echo CRM implementation completed!
echo Check the generated code and create a pull request.
pause