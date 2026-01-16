# Frontend Guide

The frontend is a **Next.js 15** application using the **App Router**.

## Project Structure
- `app/`: Contains routes and pages.
    - `page.tsx`: The main landing page.
    - `layout.tsx`: Global layout (providers, fonts).
- `components/`: Reusable React components.
    - `site-header.tsx`: Navigation bar.
    - `hero-section.tsx`: Landing page hero.
    - `scanners-section.tsx`, `features-section.tsx`, etc.
    - `ui/`: Radix UI primitives (buttons, dialogs, etc.).
- `lib/`: Utility functions (utils.ts).
- `public/`: Static assets (images, icons).

## Key Components

### UI Library
We use **shadcn/ui**, which is a collection of re-usable components built with **Radix UI** and **Tailwind CSS**. 
Components are located in `components/ui` and include:
- Buttons, Dialogs, Inputs, Cards
- Toasts (Sonner) for notifications

### Styling
Styling is handled via **Tailwind CSS**.
- Configuration: `tailwind.config.ts` (or mapped in generic config)
- Global styles: `app/globals.css`
- Dark mode is supported via `next-themes`.

## State Management
- **Local State**: `useState` / `useReducer` for component-level logic.
- **Server State**: Data fetching is primarily done via Server Actions or `fetch` calls in Client Components.

## Important Scripts
- `npm run dev`: Starts the development server.
- `npm run build`: Builds the application for production.
- `npm run start`: Starts the production server.
- `npm run lint`: Runs ESLint check.
