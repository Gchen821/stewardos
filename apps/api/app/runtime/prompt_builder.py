from app.runtime.control_agent_loader import ControlAgentAsset
from app.schemas.runtime import (
    ButlerBindingSnapshot,
    ButlerExecutionRecord,
    ButlerPlan,
    CapabilityResolution,
    RuntimeAsset,
)


class PromptBuilder:
    def build_planner_prompt(
        self,
        controller: ControlAgentAsset,
        goal: str,
        binding_snapshot: ButlerBindingSnapshot,
        planner_memory: list[str],
        candidate_capabilities: list[CapabilityResolution],
        candidate_tools: list[RuntimeAsset],
        blocked_codes: set[str],
    ) -> str:
        lines = [
            controller.prompt.strip(),
            "",
            "Execution Context:",
            f"- Goal: {goal}",
            f"- Bound agent ids: {binding_snapshot.agent_ids or '[]'}",
            f"- Bound skill ids: {binding_snapshot.skill_ids or '[]'}",
            f"- Bound tool ids: {binding_snapshot.tool_ids or '[]'}",
            f"- Planner memory: {planner_memory[-5:] or '[]'}",
            f"- Blocked asset codes: {sorted(blocked_codes) or '[]'}",
            "Candidate agents:",
        ]
        if candidate_capabilities:
            for capability in candidate_capabilities:
                lines.append(
                    f"- {capability.agent.code}: {capability.agent.name}; "
                    f"skills={[item.code for item in capability.skills]}; "
                    f"tools={[item.code for item in capability.unique_tools]}"
                )
        else:
            lines.append("- None")
        lines.append("Candidate tools:")
        if candidate_tools:
            for tool in candidate_tools:
                lines.append(f"- {tool.code}: {tool.name}; description={tool.description}")
        else:
            lines.append("- None")
        return "\n".join(lines)

    def build_reflection_prompt(
        self,
        controller: ControlAgentAsset,
        goal: str,
        plan: ButlerPlan,
        executions: list[ButlerExecutionRecord],
        repeated_plan: bool,
    ) -> str:
        lines = [
            controller.prompt.strip(),
            "",
            "Execution Context:",
            f"- Goal: {goal}",
            f"- Plan summary: {plan.summary}",
            f"- Repeated plan: {repeated_plan}",
            "Execution records:",
        ]
        if executions:
            for record in executions:
                lines.append(
                    f"- {record.asset_code}: status={record.status}; detail={record.detail}; error={record.error or ''}"
                )
        else:
            lines.append("- None")
        return "\n".join(lines)

    def build_agent_system_prompt(self, capability: CapabilityResolution) -> str:
        agent_manifest = capability.agent.manifest
        lines = [
            f"Agent: {capability.agent.name}",
            f"Description: {agent_manifest.get('description', capability.agent.description)}",
            "Available skills:",
        ]
        if capability.skills:
            for skill in capability.skills:
                exposure = skill.manifest.get("llm_exposure", {})
                lines.append(f"- {skill.name}: {exposure.get('short_desc') or skill.description}")
        else:
            lines.append("- None")
        lines.append("Direct tools:")
        if capability.direct_tools:
            for tool in capability.direct_tools:
                exposure = tool.manifest.get("llm_exposure", {})
                lines.append(f"- {tool.name}: {exposure.get('short_desc') or tool.description}")
        else:
            lines.append("- None")
        lines.append("Do not assume skill-internal tools are globally available unless entering that skill stage.")
        return "\n".join(lines)

    def build_skill_execution_prompt(self, capability: CapabilityResolution, skill_code: str) -> str:
        skill = next((item for item in capability.skills if item.code == skill_code), None)
        if skill is None:
            raise ValueError(f"skill {skill_code} not found in capability resolution")
        lines = [
            f"Skill execution: {skill.name}",
            f"Description: {skill.manifest.get('description', skill.description)}",
            f"When to use: {skill.manifest.get('llm_exposure', {}).get('when_to_use', '')}",
            "Skill tools:",
        ]
        for tool in capability.skill_tools.get(skill.code, []):
            exposure = tool.manifest.get("llm_exposure", {})
            lines.append(
                f"- {tool.name}: {exposure.get('short_desc') or tool.description}; args={exposure.get('args_desc', '')}; caution={exposure.get('caution', '')}"
            )
        if not capability.skill_tools.get(skill.code):
            lines.append("- None")
        return "\n".join(lines)
