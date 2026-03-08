import { useState } from 'react';
import { authApi } from '../../api/quipClient';

interface LoginPageProps {
  onLogin: () => void;
}

export function LoginPage({ onLogin }: LoginPageProps) {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        if (!name.trim()) {
          setError('名前を入力してください');
          setLoading(false);
          return;
        }
        await authApi.register(name, email, password);
      } else {
        await authApi.login(email, password);
      }
      onLogin();
    } catch (err: any) {
      setError(err.message || 'エラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <h1>Quip-SharePoint</h1>
          <p>{isRegister ? 'アカウント作成' : 'ログイン'}</p>
        </div>
        <form onSubmit={handleSubmit} className="login-form">
          {isRegister && (
            <div className="form-group">
              <label htmlFor="name">名前</label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your Name"
                required={isRegister}
                autoComplete="name"
              />
            </div>
          )}
          <div className="form-group">
            <label htmlFor="email">メールアドレス</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              autoComplete="email"
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">パスワード</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={6}
              autoComplete={isRegister ? 'new-password' : 'current-password'}
            />
          </div>
          {error && <div className="login-error">{error}</div>}
          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? '...' : isRegister ? '登録' : 'ログイン'}
          </button>
        </form>
        <div className="login-toggle">
          <button onClick={() => { setIsRegister(!isRegister); setError(''); }}>
            {isRegister ? 'すでにアカウントがある場合はログイン' : 'アカウントを作成'}
          </button>
        </div>
      </div>
    </div>
  );
}
