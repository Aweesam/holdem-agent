/**
 * Browser-safe logging configuration for the holdem dashboard.
 * Provides console logging in browser and file logging on server.
 */

// Simple interface for consistent logging
interface LogMeta {
  [key: string]: unknown;
}

interface Logger {
  error: (message: string, meta?: LogMeta) => void;
  warn: (message: string, meta?: LogMeta) => void;
  info: (message: string, meta?: LogMeta) => void;
  debug: (message: string, meta?: LogMeta) => void;
  apiCall: (endpoint: string, method?: string, meta?: LogMeta) => void;
  websocket: (event: string, meta?: LogMeta) => void;
  component: (component: string, event: string, meta?: LogMeta) => void;
  performance: (operation: string, duration: number, meta?: LogMeta) => void;
}

// Browser-safe logger implementation
class BrowserLogger implements Logger {
  private isServer = typeof window === 'undefined';
  private serverLogger: unknown = null;

  constructor() {
    if (this.isServer) {
      this.initServerLogger();
    }
  }

  private initServerLogger() {
    try {
      // Dynamic require to avoid webpack bundling issues
      const winston = eval('require')('winston');
      const path = eval('require')('path');
      const fs = eval('require')('fs');
      
      // Create log directory
      const logDir = path.resolve(process.cwd(), '../../logs/dashboard');
      try {
        fs.mkdirSync(logDir, { recursive: true });
      } catch {
        // Directory might already exist
      }

      this.serverLogger = winston.createLogger({
        level: process.env.DASH_LOG_LEVEL || 'info',
        format: winston.format.combine(
          winston.format.timestamp(),
          winston.format.errors({ stack: true }),
          winston.format.json()
        ),
        transports: [
          new winston.transports.File({
            filename: path.join(logDir, 'dashboard.log'),
            maxsize: 10 * 1024 * 1024, // 10MB
            maxFiles: 14
          }),
          new winston.transports.File({
            filename: path.join(logDir, 'error.log'),
            level: 'error',
            maxsize: 10 * 1024 * 1024,
            maxFiles: 30
          })
        ]
      });

      // Add console transport in development
      if (process.env.NODE_ENV !== 'production' && this.serverLogger && typeof this.serverLogger === 'object' && 'add' in this.serverLogger) {
        (this.serverLogger as { add: (transport: unknown) => void }).add(new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.simple()
          )
        }));
      }
    } catch (error) {
      console.warn('Failed to initialize server logger, falling back to console:', error);
    }
  }

  private formatMessage(level: string, message: string, meta?: LogMeta): string {
    const timestamp = new Date().toISOString();
    const metaStr = meta ? ` ${JSON.stringify(meta)}` : '';
    return `[${timestamp}] ${level.toUpperCase()}: ${message}${metaStr}`;
  }

  error(message: string, meta?: LogMeta) {
    if (this.serverLogger && typeof this.serverLogger === 'object' && 'error' in this.serverLogger) {
      (this.serverLogger as { error: (msg: string, meta?: LogMeta) => void }).error(message, meta);
    } else {
      console.error(this.formatMessage('error', message, meta));
    }
    
    // Also log to console for visibility in fatal cases
    if (meta?.fatal) {
      console.error(`🔴 DASHBOARD FATAL ERROR: ${message}`, meta);
    }
  }

  warn(message: string, meta?: LogMeta) {
    if (this.serverLogger && typeof this.serverLogger === 'object' && 'warn' in this.serverLogger) {
      (this.serverLogger as { warn: (msg: string, meta?: LogMeta) => void }).warn(message, meta);
    } else {
      console.warn(this.formatMessage('warn', message, meta));
    }
  }

  info(message: string, meta?: LogMeta) {
    if (this.serverLogger && typeof this.serverLogger === 'object' && 'info' in this.serverLogger) {
      (this.serverLogger as { info: (msg: string, meta?: LogMeta) => void }).info(message, meta);
    } else {
      console.info(this.formatMessage('info', message, meta));
    }
  }

  debug(message: string, meta?: LogMeta) {
    if (this.serverLogger && typeof this.serverLogger === 'object' && 'debug' in this.serverLogger) {
      (this.serverLogger as { debug: (msg: string, meta?: LogMeta) => void }).debug(message, meta);
    } else {
      console.debug(this.formatMessage('debug', message, meta));
    }
  }

  apiCall(endpoint: string, method: string = 'GET', meta?: LogMeta) {
    this.info(`API call: ${method} ${endpoint}`, {
      type: 'api_call',
      endpoint,
      method,
      ...meta
    });
  }

  websocket(event: string, meta?: LogMeta) {
    this.debug(`WebSocket: ${event}`, {
      type: 'websocket',
      event,
      ...meta
    });
  }

  component(component: string, event: string, meta?: LogMeta) {
    this.debug(`Component ${component}: ${event}`, {
      type: 'component',
      component,
      event,
      ...meta
    });
  }

  performance(operation: string, duration: number, meta?: LogMeta) {
    this.info(`Performance: ${operation} took ${duration}ms`, {
      type: 'performance',
      operation,
      duration,
      ...meta
    });
  }
}

// Create single logger instance
export const dashboardLogger = new BrowserLogger();

// Setup global error handlers
if (typeof window !== 'undefined') {
  // Browser environment
  window.addEventListener('error', (event) => {
    dashboardLogger.error('Unhandled JavaScript error', {
      fatal: true,
      error: event.error?.message || event.message,
      stack: event.error?.stack,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno
    });
  });

  window.addEventListener('unhandledrejection', (event) => {
    dashboardLogger.error('Unhandled Promise rejection', {
      fatal: true,
      reason: event.reason?.toString(),
      stack: event.reason?.stack
    });
  });
} else {
  // Node.js environment (Next.js server-side)
  process.on('uncaughtException', (error) => {
    dashboardLogger.error('Uncaught Exception', {
      fatal: true,
      error: error.message,
      stack: error.stack
    });
    console.error('🔴 DASHBOARD FATAL ERROR:', error);
  });

  process.on('unhandledRejection', (reason, promise) => {
    dashboardLogger.error('Unhandled Rejection', {
      fatal: true,
      reason: reason?.toString(),
      stack: (reason as Error)?.stack,
      promise: promise.toString()
    });
    console.error('🔴 DASHBOARD FATAL ERROR: Unhandled Promise Rejection:', reason);
  });
}

export default dashboardLogger;