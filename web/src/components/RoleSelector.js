import React, { useState, useEffect } from 'react';
import { Select, Input, Button, message, Card, Radio, Space, Modal, Form, Popconfirm, Tooltip } from 'antd';
import { DeleteOutlined, QuestionCircleOutlined, SaveOutlined } from '@ant-design/icons';
import axios from 'axios';

const { TextArea } = Input;

const RoleSelector = ({ onRoleSelected, apiBaseUrl }) => {
  const [roles, setRoles] = useState({});
  const [selectedRole, setSelectedRole] = useState('assistant');
  const [customPrompt, setCustomPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingRoles, setLoadingRoles] = useState(true);
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [customRoleName, setCustomRoleName] = useState('');
  const [savingRole, setSavingRole] = useState(false);
  const [deletingRole, setDeletingRole] = useState('');

  // 内置角色列表，不允许删除
  const builtInRoles = ["assistant", "programmer", "creative"];

  // 获取可用角色
  useEffect(() => {
    if (!apiBaseUrl) return;

    setLoadingRoles(true);
    axios.get(`${apiBaseUrl}/api/role`)
      .then(response => {
        setRoles(response.data.predefined_roles);
        setSelectedRole(response.data.current_role);
        setLoadingRoles(false);
      })
      .catch(error => {
        console.error('获取角色失败:', error);
        message.error('获取角色列表失败');
        setLoadingRoles(false);
      });
  }, [apiBaseUrl]);

  // 设置角色
  const handleSetRole = () => {
    if (!apiBaseUrl) return;

    setLoading(true);

    const data = {
      type: selectedRole,
      custom_prompt: selectedRole === 'custom' ? customPrompt : ''
    };

    axios.post(`${apiBaseUrl}/api/role`, data)
      .then(response => {
        message.success('角色设置成功');
        if (onRoleSelected) {
          onRoleSelected(response.data);
        }
      })
      .catch(error => {
        console.error('设置角色失败:', error);
        message.error('设置角色失败');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  // 保存自定义角色
  const handleSaveCustomRole = () => {
    if (!apiBaseUrl || !customRoleName.trim() || !customPrompt.trim()) {
      message.error('角色名称和提示词不能为空');
      return;
    }

    setSavingRole(true);

    axios.post(`${apiBaseUrl}/api/role/save`, {
      name: customRoleName.trim(),
      prompt: customPrompt.trim()
    })
      .then(response => {
        message.success(`角色 "${customRoleName}" 已保存`);
        // 更新角色列表
        setRoles(response.data.predefined_roles);
        // 关闭保存对话框
        setSaveModalVisible(false);
        setCustomRoleName('');
      })
      .catch(error => {
        console.error('保存角色失败:', error);
        message.error('保存角色失败: ' + (error.response?.data?.error || error.message));
      })
      .finally(() => {
        setSavingRole(false);
      });
  };

  // 删除预设角色
  const handleDeleteRole = (roleName) => {
    if (!apiBaseUrl || !roleName) return;

    setDeletingRole(roleName);

    axios.post(`${apiBaseUrl}/api/role/delete`, {
      name: roleName
    })
      .then(response => {
        message.success(`角色 "${roleName}" 已删除`);
        // 更新角色列表
        setRoles(response.data.predefined_roles);
        // 如果当前选中的角色被删除，则切换到默认角色
        if (selectedRole === roleName) {
          setSelectedRole('assistant');
        }
      })
      .catch(error => {
        console.error('删除角色失败:', error);
        message.error('删除角色失败: ' + (error.response?.data?.error || error.message));
      })
      .finally(() => {
        setDeletingRole('');
      });
  };

  const roleDescriptions = {
    assistant: "美团AI助手，提供专业、准确、有帮助的回答",
    programmer: "经验丰富的程序员，擅长解决各种编程问题",
    creative: "创意顾问，擅长提供创新的想法和解决方案"
  };

  return (
    <Card 
      title={
        <div className="role-card-title">
          <span>选择AI角色</span>
          <div className="role-management-tip">
            <span>非内置角色可删除</span>
            <DeleteOutlined style={{ color: 'red', margin: '0 4px' }} />
          </div>
        </div>
      } 
      className="role-selector-card"
    >
      <div className="role-selector">
        {loadingRoles ? (
          <div className="loading-roles">加载角色中...</div>
        ) : (
          <>
            <Radio.Group 
              value={selectedRole} 
              onChange={e => setSelectedRole(e.target.value)}
              className="role-radio-group"
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                {Object.keys(roles).map(key => (
                  <div key={key} className="role-item">
                    <Radio value={key}>
                      <div className="role-option">
                        <span className="role-name">{roles[key]}</span>
                        <span className="role-description">{roleDescriptions[key] || '自定义角色'}</span>
                      </div>
                    </Radio>
                    {!builtInRoles.includes(key) ? (
                      <Popconfirm
                        title="删除角色"
                        description={`确定要删除角色 "${roles[key]}" 吗？`}
                        onConfirm={() => handleDeleteRole(key)}
                        okText="确定"
                        cancelText="取消"
                        icon={<QuestionCircleOutlined style={{ color: 'red' }} />}
                      >
                        <Button 
                          type="text" 
                          danger 
                          icon={<DeleteOutlined />} 
                          size="small"
                          loading={deletingRole === key}
                          className="delete-role-button"
                        >
                          删除
                        </Button>
                      </Popconfirm>
                    ) : (
                      <span className="built-in-role-tag">内置</span>
                    )}
                  </div>
                ))}
                <Radio value="custom">
                  <div className="role-option">
                    <span className="role-name">自定义角色</span>
                    <span className="role-description">自定义AI的角色和行为</span>
                  </div>
                </Radio>
              </Space>
            </Radio.Group>

            {selectedRole === 'custom' && (
              <div className="custom-role-input">
                <TextArea
                  placeholder="请输入自定义角色提示词，例如：你是一位专业的旅游顾问，擅长推荐旅游路线和景点..."
                  value={customPrompt}
                  onChange={e => setCustomPrompt(e.target.value)}
                  rows={4}
                  style={{ marginTop: 16, marginBottom: 16 }}
                />
                <div className="custom-role-actions">
                  <Button 
                    type="primary" 
                    icon={<SaveOutlined />}
                    onClick={() => setSaveModalVisible(true)}
                    disabled={!customPrompt.trim()}
                    style={{ marginRight: 8 }}
                  >
                    保存为预设角色
                  </Button>
                  <Button 
                    type="default" 
                    onClick={handleSetRole}
                    loading={loading}
                    disabled={!customPrompt.trim()}
                  >
                    临时使用
                  </Button>
                </div>
              </div>
            )}

            {selectedRole !== 'custom' && (
              <Button 
                type="primary" 
                onClick={handleSetRole}
                loading={loading}
                className="confirm-role-button"
              >
                确认选择
              </Button>
            )}

            {/* 保存自定义角色的对话框 */}
            <Modal
              title="保存自定义角色"
              open={saveModalVisible}
              onOk={handleSaveCustomRole}
              onCancel={() => setSaveModalVisible(false)}
              confirmLoading={savingRole}
              okText="保存"
              cancelText="取消"
            >
              <Form layout="vertical">
                <Form.Item 
                  label="角色名称" 
                  required 
                  help="请输入一个简短的名称，用于在角色列表中显示"
                >
                  <Input
                    placeholder="例如：旅游顾问"
                    value={customRoleName}
                    onChange={e => setCustomRoleName(e.target.value)}
                    maxLength={20}
                  />
                </Form.Item>
                <Form.Item label="角色提示词">
                  <div className="prompt-preview">
                    {customPrompt}
                  </div>
                </Form.Item>
              </Form>
            </Modal>
          </>
        )}
      </div>
    </Card>
  );
};

export default RoleSelector;