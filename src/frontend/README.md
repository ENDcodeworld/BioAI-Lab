# BioAI-Lab Frontend

React + TypeScript frontend application for BioAI-Lab platform.

## Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable components
│   ├── pages/           # Page components
│   ├── hooks/           # Custom hooks
│   ├── stores/          # State management (Zustand)
│   ├── api/             # API client
│   ├── utils/           # Utilities
│   └── styles/          # Styles
├── public/              # Static assets
└── package.json
```

## Tech Stack

- **Framework**: React 18 + TypeScript
- **UI Library**: Ant Design 5
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Build Tool**: Vite
- **Styling**: CSS Modules / Styled Components

## Environment Variables

Create `.env` file:

```bash
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=BioAI-Lab
```
