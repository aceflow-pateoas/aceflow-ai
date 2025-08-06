# Changelog

## [1.1.0] - 2025-08-06

### 🎉 Major Features Added
- **Enhanced .clinerules System**: Complete overhaul of AI Agent prompt system
  - Added 5 comprehensive prompt files instead of single file
  - `system_prompt.md`: Enhanced AI Agent identity and behavior rules
  - `aceflow_integration.md`: Complete AceFlow integration guidelines
  - `spec_summary.md`: Quick reference to AceFlow v3.0 specification
  - `spec_query_helper.md`: SPEC document query assistance
  - `quality_standards.md`: Comprehensive quality standards based on SPEC Chapter 8

### ✨ Improvements
- **SPEC Integration**: Full integration with AceFlow v3.0 specification
- **Project-Specific Configuration**: All generated files now include project name and mode
- **Quality Standards**: Implemented complete quality gate system (DG1-DG5)
- **Documentation**: Enhanced documentation with detailed usage examples
- **Template System**: Improved template generation with better structure

### 🔧 Technical Changes
- Refactored `_initialize_project_structure` method for enhanced file generation
- Added 5 new generation methods for comprehensive prompt system
- Improved error handling and encoding compatibility
- Enhanced build hooks for better template synchronization

### 🐛 Bug Fixes
- Fixed encoding issues in build hooks
- Resolved template synchronization problems
- Improved cross-platform compatibility

### 📚 Documentation
- Updated README with new features
- Added comprehensive usage examples
- Improved API documentation

## [1.0.7] - Previous Version
- Basic .clinerules functionality
- Standard MCP server implementation