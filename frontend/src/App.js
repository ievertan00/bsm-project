import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import { Layout, Menu, Button, Space, ConfigProvider } from 'antd';
import { 
  DashboardOutlined, 
  DatabaseOutlined, 
  ImportOutlined, 
  LogoutOutlined,
  UserOutlined
} from '@ant-design/icons';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DataProvider } from './DataContext';
import Dashboard from './pages/Dashboard';
import DataManagement from './pages/DataManagement';
import ImportDataPage from './pages/ImportDataPage';
import Login from './pages/Login';

const { Header, Content, Footer } = Layout;

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) return null;
  if (!user) return <Navigate to="/login" />;
  
  return children;
};

const Navigation = () => {
  const { logout, user } = useAuth();
  
  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: <Link to="/">Dashboard</Link>,
    },
    {
      key: 'data',
      icon: <DatabaseOutlined />,
      label: <Link to="/data">Data Management</Link>,
    },
    {
      key: 'import',
      icon: <ImportOutlined />,
      label: <Link to="/import">Import Data</Link>,
    },
  ];

  return (
    <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <div style={{ color: 'white', fontWeight: 'bold', fontSize: '18px', marginRight: '32px' }}>
          BSM REPRODUCTION
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          defaultSelectedKeys={['dashboard']}
          items={menuItems}
          style={{ flex: 1, minWidth: 0 }}
        />
      </div>
      <Space>
        <span style={{ color: 'white' }}>
          <UserOutlined /> {user?.username}
        </span>
        <Button 
          type="text" 
          icon={<LogoutOutlined />} 
          onClick={logout}
          style={{ color: 'white' }}
        >
          Logout
        </Button>
      </Space>
    </Header>
  );
};

function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <AuthProvider>
        <DataProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <Layout className="layout" style={{ minHeight: '100vh' }}>
                      <Navigation />
                      <Content style={{ padding: '0 50px' }}>
                        <div className="site-layout-content" style={{ margin: '16px 0' }}>
                          <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/data" element={<DataManagement />} />
                            <Route path="/import" element={<ImportDataPage />} />
                            <Route path="*" element={<Navigate to="/" />} />
                          </Routes>
                        </div>
                      </Content>
                      <Footer style={{ textAlign: 'center' }}>
                        BSM Reproduction ©2024 Created by Gemini CLI
                      </Footer>
                    </Layout>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </Router>
        </DataProvider>
      </AuthProvider>
    </ConfigProvider>
  );
}

export default App;
