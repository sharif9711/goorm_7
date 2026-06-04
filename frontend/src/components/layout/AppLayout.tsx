import {
  DashboardOutlined,
  FileTextOutlined,
  KeyOutlined,
  LogoutOutlined,
  MoonOutlined,
  SearchOutlined,
  SunOutlined,
  UserOutlined,
  VideoCameraOutlined,
  YoutubeOutlined,
} from '@ant-design/icons';
import { Layout, Menu, Button, Avatar, Dropdown, theme } from 'antd';
import { motion } from 'framer-motion';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore, useThemeStore } from '@/stores/authStore';

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: '/trends', icon: <SearchOutlined />, label: 'Trend Explorer' },
  { key: '/channels', icon: <YoutubeOutlined />, label: 'Channel Analyzer' },
  { key: '/keywords', icon: <KeyOutlined />, label: 'Keyword Explorer' },
  { key: '/reports', icon: <FileTextOutlined />, label: 'Reports' },
];

export default function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { isDark, toggleTheme } = useThemeStore();
  const { token: { colorBgContainer } } = theme.useToken();

  const selectedKey = menuItems.find((item) =>
    item.key === '/' ? location.pathname === '/' : location.pathname.startsWith(item.key)
  )?.key || '/';

  const userMenu = {
    items: [
      { key: 'logout', icon: <LogoutOutlined />, label: 'Logout', onClick: () => { logout(); navigate('/login'); } },
    ],
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        breakpoint="lg"
        collapsedWidth={0}
        style={{ background: isDark ? '#141414' : '#001529' }}
      >
        <div style={{ padding: '16px', textAlign: 'center' }}>
          <VideoCameraOutlined style={{ fontSize: 28, color: '#ff4d4f' }} />
          <div style={{ color: '#fff', fontWeight: 600, marginTop: 8, fontSize: 13 }}>
            Trend Agent
          </div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 24px', background: colorBgContainer, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 12 }}>
          <Button
            type="text"
            icon={isDark ? <SunOutlined /> : <MoonOutlined />}
            onClick={toggleTheme}
          />
          <Dropdown menu={userMenu}>
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar icon={<UserOutlined />} />
              <span>{user?.name}</span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: '16px', overflow: 'auto' }}>
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Outlet />
          </motion.div>
        </Content>
      </Layout>
    </Layout>
  );
}
