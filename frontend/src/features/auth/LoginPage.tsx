import { GoogleOutlined, LockOutlined, MailOutlined, UserOutlined } from '@ant-design/icons';
import { Alert, Button, Card, Form, Input, Tabs, Typography } from 'antd';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@/api';
import { useAuthStore } from '@/stores/authStore';

const { Title, Text } = Typography;

export default function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (values: { email: string; password: string }) => {
    setLoading(true);
    setError('');
    try {
      const { data } = await authApi.login(values.email, values.password);
      setAuth(data.access_token, data.user);
      navigate('/');
    } catch {
      setError('로그인에 실패했습니다. 이메일과 비밀번호를 확인해주세요.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values: { email: string; name: string; password: string }) => {
    setLoading(true);
    setError('');
    try {
      const { data } = await authApi.register(values.email, values.name, values.password);
      setAuth(data.access_token, data.user);
      navigate('/');
    } catch {
      setError('회원가입에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    setError('Google OAuth는 GOOGLE_CLIENT_ID 설정 후 사용 가능합니다.');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16, background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)' }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ width: '100%', maxWidth: 420 }}>
        <Card>
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <Title level={2} style={{ marginBottom: 4 }}>YouTube Trend Agent</Title>
            <Text type="secondary">AI 기반 YouTube 트렌드 리서치</Text>
          </div>

          {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} />}

          <Button block icon={<GoogleOutlined />} size="large" onClick={handleGoogleLogin} style={{ marginBottom: 16 }}>
            Google로 로그인
          </Button>

          <Tabs
            items={[
              {
                key: 'login',
                label: '로그인',
                children: (
                  <Form onFinish={handleLogin} layout="vertical">
                    <Form.Item name="email" rules={[{ required: true, type: 'email' }]}>
                      <Input prefix={<MailOutlined />} placeholder="이메일" size="large" />
                    </Form.Item>
                    <Form.Item name="password" rules={[{ required: true, min: 8 }]}>
                      <Input.Password prefix={<LockOutlined />} placeholder="비밀번호" size="large" />
                    </Form.Item>
                    <Button type="primary" htmlType="submit" block size="large" loading={loading}>
                      로그인
                    </Button>
                  </Form>
                ),
              },
              {
                key: 'register',
                label: '회원가입',
                children: (
                  <Form onFinish={handleRegister} layout="vertical">
                    <Form.Item name="name" rules={[{ required: true }]}>
                      <Input prefix={<UserOutlined />} placeholder="이름" size="large" />
                    </Form.Item>
                    <Form.Item name="email" rules={[{ required: true, type: 'email' }]}>
                      <Input prefix={<MailOutlined />} placeholder="이메일" size="large" />
                    </Form.Item>
                    <Form.Item name="password" rules={[{ required: true, min: 8 }]}>
                      <Input.Password prefix={<LockOutlined />} placeholder="비밀번호 (8자 이상)" size="large" />
                    </Form.Item>
                    <Button type="primary" htmlType="submit" block size="large" loading={loading}>
                      회원가입
                    </Button>
                  </Form>
                ),
              },
            ]}
          />
        </Card>
      </motion.div>
    </div>
  );
}
