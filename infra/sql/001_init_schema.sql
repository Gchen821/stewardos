CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  display_name VARCHAR(128) NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  refresh_token_hash VARCHAR(255) NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(64) UNIQUE NOT NULL,
  name VARCHAR(128) NOT NULL,
  description TEXT
);

CREATE TABLE IF NOT EXISTS user_role_bindings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  UNIQUE (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(128) UNIQUE NOT NULL,
  name VARCHAR(128) NOT NULL,
  description TEXT,
  scope_type VARCHAR(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS role_permission_bindings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
  UNIQUE (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  name VARCHAR(128) NOT NULL,
  code VARCHAR(64) UNIQUE NOT NULL,
  type VARCHAR(32) NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'draft',
  description TEXT,
  system_prompt TEXT,
  icon VARCHAR(512),
  risk_level VARCHAR(8) NOT NULL DEFAULT 'L1',
  allow_chat_select BOOLEAN NOT NULL DEFAULT TRUE,
  is_builtin BOOLEAN NOT NULL DEFAULT FALSE,
  version VARCHAR(32) NOT NULL DEFAULT '0.1.0',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(128) NOT NULL,
  code VARCHAR(64) UNIQUE NOT NULL,
  category VARCHAR(64) NOT NULL DEFAULT 'general',
  description TEXT,
  version VARCHAR(32) NOT NULL DEFAULT '0.1.0',
  entrypoint VARCHAR(255),
  input_schema_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  output_schema_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  risk_level VARCHAR(8) NOT NULL DEFAULT 'L1',
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tools (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(128) NOT NULL,
  code VARCHAR(64) UNIQUE NOT NULL,
  type VARCHAR(64) NOT NULL DEFAULT 'builtin',
  description TEXT,
  version VARCHAR(32) NOT NULL DEFAULT '0.1.0',
  entrypoint VARCHAR(255),
  risk_level VARCHAR(8) NOT NULL DEFAULT 'L1',
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_skill_bindings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  sort_order INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (agent_id, skill_id)
);

CREATE TABLE IF NOT EXISTS skill_tool_bindings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  tool_id UUID NOT NULL REFERENCES tools(id) ON DELETE CASCADE,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  sort_order INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (skill_id, tool_id)
);

CREATE TABLE IF NOT EXISTS agent_status_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  old_status VARCHAR(16) NOT NULL,
  new_status VARCHAR(16) NOT NULL,
  operator_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id UUID NOT NULL UNIQUE REFERENCES agents(id) ON DELETE CASCADE,
  allow_online BOOLEAN NOT NULL DEFAULT FALSE,
  allow_chat_select BOOLEAN NOT NULL DEFAULT TRUE,
  max_risk_level VARCHAR(8) NOT NULL DEFAULT 'L1',
  skill_whitelist_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skill_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_id UUID NOT NULL UNIQUE REFERENCES skills(id) ON DELETE CASCADE,
  allowed_roles_json JSONB NOT NULL DEFAULT '[]'::jsonb,
  risk_level VARCHAR(8) NOT NULL DEFAULT 'L1',
  requires_confirm BOOLEAN NOT NULL DEFAULT FALSE,
  enabled BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  target_type VARCHAR(16) NOT NULL,
  target_id UUID,
  title VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  sender_role VARCHAR(16) NOT NULL,
  sender_id UUID,
  content TEXT NOT NULL,
  message_type VARCHAR(16) NOT NULL DEFAULT 'text',
  metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS job_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
  conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'queued',
  input_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  output_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  error_message TEXT,
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  entity_type VARCHAR(32) NOT NULL,
  entity_id UUID,
  action VARCHAR(64) NOT NULL,
  detail_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  ip VARCHAR(64),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS llm_providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(64) UNIQUE NOT NULL,
  name VARCHAR(128) NOT NULL,
  base_url VARCHAR(512),
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS llm_provider_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id UUID NOT NULL REFERENCES llm_providers(id) ON DELETE CASCADE,
  key_name VARCHAR(128) NOT NULL,
  encrypted_key TEXT NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS llm_models (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id UUID NOT NULL REFERENCES llm_providers(id) ON DELETE CASCADE,
  model_code VARCHAR(128) NOT NULL,
  model_name VARCHAR(128) NOT NULL,
  context_window INT,
  input_price NUMERIC(12, 6),
  output_price NUMERIC(12, 6),
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (provider_id, model_code)
);

CREATE TABLE IF NOT EXISTS agent_model_bindings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  model_id UUID NOT NULL REFERENCES llm_models(id) ON DELETE CASCADE,
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  temperature NUMERIC(3, 2),
  top_p NUMERIC(3, 2),
  max_tokens INT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (agent_id, model_id)
);

CREATE TABLE IF NOT EXISTS llm_routing_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule_name VARCHAR(128) NOT NULL,
  target_scope VARCHAR(32) NOT NULL,
  target_id UUID,
  priority INT NOT NULL DEFAULT 100,
  condition_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  model_id UUID REFERENCES llm_models(id) ON DELETE SET NULL,
  fallback_model_id UUID REFERENCES llm_models(id) ON DELETE SET NULL,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS llm_call_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
  message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
  provider_id UUID REFERENCES llm_providers(id) ON DELETE SET NULL,
  model_id UUID REFERENCES llm_models(id) ON DELETE SET NULL,
  prompt_tokens INT,
  completion_tokens INT,
  latency_ms INT,
  status VARCHAR(16) NOT NULL DEFAULT 'success',
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_agents_owner_status ON agents(owner_user_id, status);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_skills_category_status ON skills(category, status);
CREATE INDEX IF NOT EXISTS idx_agent_skill_enabled ON agent_skill_bindings(agent_id, enabled);
CREATE INDEX IF NOT EXISTS idx_skill_tool_enabled ON skill_tool_bindings(skill_id, enabled);
CREATE INDEX IF NOT EXISTS idx_agent_status_history ON agent_status_history(agent_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_user_target_updated ON conversations(user_id, target_type, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_job_runs_conversation ON job_runs(conversation_id);
CREATE INDEX IF NOT EXISTS idx_job_runs_status_created ON job_runs(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_time ON audit_logs(entity_type, entity_id, created_at DESC);

INSERT INTO roles (code, name, description) VALUES
  ('admin', '管理员', '平台管理员'),
  ('user', '普通用户', '默认业务用户'),
  ('system', '系统角色', '系统内部角色')
ON CONFLICT (code) DO NOTHING;

INSERT INTO permissions (code, name, description, scope_type) VALUES
  ('system.model.manage', '模型管理', '管理模型与路由', 'api'),
  ('agent.manage', 'Agent 管理', '管理 Agent 仓库与状态', 'api'),
  ('skill.manage', 'Skill 管理', '管理 Skill 仓库与状态', 'api'),
  ('audit.read', '审计读取', '读取审计与执行日志', 'api'),
  ('chat.use_agent', '聊天调用 Agent', '在聊天中使用 Agent', 'api')
ON CONFLICT (code) DO NOTHING;

INSERT INTO users (email, password_hash, display_name, status)
VALUES ('admin@steward.local', 'dev_only_hash_change_me', 'Steward Admin', 'active')
ON CONFLICT (email) DO NOTHING;

INSERT INTO agents (name, code, type, status, description, allow_chat_select, risk_level, is_builtin)
VALUES ('主控管家', 'butler', 'butler', 'offline', '默认主控管家 Agent', TRUE, 'L1', TRUE)
ON CONFLICT (code) DO NOTHING;

INSERT INTO skills (name, code, category, description, status, risk_level)
VALUES
  ('知识检索', 'knowledge_search', 'search', '检索并摘要公开知识', 'active', 'L1'),
  ('结构化笔记', 'structured_note', 'memory', '写入结构化笔记', 'active', 'L1')
ON CONFLICT (code) DO NOTHING;

INSERT INTO tools (name, code, type, description, status, risk_level)
VALUES
  ('Knowledge Query', 'knowledge_query', 'builtin', '底层知识查询工具', 'active', 'L1'),
  ('Note Writer', 'note_writer', 'builtin', '结构化笔记写入工具', 'active', 'L1')
ON CONFLICT (code) DO NOTHING;
