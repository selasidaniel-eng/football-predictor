# Football Bet Predictor - Frontend

React + TypeScript frontend for the football match prediction website.

## Tech Stack

- **Framework:** React 18+
- **Language:** TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **Routing:** React Router v6
- **State Management:** React Context / Zustand (TBD)
- **Charts:** Recharts
- **UI Components:** Headless UI / Radix UI

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── MatchCard.tsx
│   │   ├── PredictionDisplay.tsx
│   │   └── [...other components]
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── MatchDetail.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   └── [...other pages]
│   ├── services/
│   │   ├── api.ts          # Axios client
│   │   └── types.ts        # TypeScript types
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useLiveScore.ts
│   │   └── [...other hooks]
│   ├── styles/
│   │   ├── globals.css
│   │   └── tailwind.css
│   ├── App.tsx
│   ├── index.tsx
│   └── vite-env.d.ts
├── public/
│   └── [static assets]
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── Dockerfile
└── README.md              # This file
```

## Installation

### Prerequisites

- Node.js 18+ and npm 9+
- Yarn or npm

### Local Setup

1. **Navigate to frontend folder**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Create .env file** (copy from root)
   ```bash
   cp ../.env.example .env.local
   ```
   Edit `.env.local` with your settings

4. **Start development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

   Application will be available at `http://localhost:5173`

## Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Run linting
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

### Project Configuration

- **Vite Config:** `vite.config.ts`
- **TypeScript Config:** `tsconfig.json`
- **Tailwind Config:** `tailwind.config.js`
- **Environment Variables:** `.env.local`

## API Integration

API client configured in `src/services/api.ts`:

```typescript
import { api } from '@/services/api'

// Example: Fetch upcoming matches
const { data } = await api.get('/matches/upcoming', {
  params: { league: 'PL', days: 7 }
})
```

API base URL is set from `VITE_API_URL` environment variable.

## Styling

Using Tailwind CSS for styling. Configuration in `tailwind.config.js`.

```tsx
// Example component
function MatchCard() {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-lg font-bold">Match Title</h3>
    </div>
  )
}
```

## Features by Page

### HomePage
- Display upcoming matches for selected leagues
- Filter by league, date
- Search by team name
- Sort by confidence/date
- Real-time score updates (polling)

### MatchDetail
- Live score display
- H2H statistics chart
- Team form trends
- Key prediction factors
- Odds comparison
- Save prediction button

### Dashboard
- Saved predictions list
- Prediction outcomes (won/lost/pending)
- Personal accuracy statistics
- ROI calculation
- Bet tracking

### Authentication
- Registration page
- Login page
- Profile/settings page
- Logout functionality

## Building for Production

```bash
# Build optimized production bundle
npm run build

# Output goes to dist/ folder
```

### Deployment (Vercel)

1. Push to GitHub
2. Connect repo to Vercel
3. Configure environment variables
4. Deploy automatically on push

## Troubleshooting

### Port 5173 already in use
```bash
npm run dev -- --port 5174
```

### API connection errors
- Check `VITE_API_URL` in `.env.local`
- Verify backend is running on configured URL
- Check CORS settings in backend

### Module not found
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build errors
```bash
# Check TypeScript
npm run type-check

# Run linter
npm run lint
```

## Performance

- Lazy load route components
- Optimize bundle size with Code Splitting
- Cache API responses
- Implement virtual scrolling for large lists

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Android)

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Follow TypeScript and ESLint rules
3. Write clean, well-documented code
4. Test changes locally
5. Submit PR with description

## Documentation

- [API Documentation](../API_DOCUMENTATION.md)
- [Requirements](../REQUIREMENTS.md)
- [Vite Guide](https://vitejs.dev)
- [React Docs](https://react.dev)
- [TypeScript Docs](https://www.typescriptlang.org)
- [Tailwind CSS Docs](https://tailwindcss.com)

## License

[To be determined]
