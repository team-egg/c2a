import react from 'react';

interface Props {
  fallback: react.ReactNode;
  children: react.ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundary extends react.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  componentDidCatch(error: Error, errorInfo: react.ErrorInfo) {}

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
