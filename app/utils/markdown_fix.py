import re


def validate_player_analysis(content):
    """
    验证玩家分析内容是否符合 sublist 格式。
    :param content: LLM 生成的文本内容
    :return: 验证结果和问题部分列表
    """
    # 正则表达式匹配玩家分析的整体格式，动态适应玩家名称（角色）的变化
    player_pattern = re.compile(
        r"- 玩家名称（角色）：.+?\n"
        r"(?:\s{3}- 关键数据：.+?\n)"
        r"(?:\s{3}- 问题分析：.+?\n)"
        r"(?:\s{3}- 改进建议：.+?\n)",
        re.DOTALL
    )

    # 分割每个玩家分析部分
    players = content.split("- 玩家名称（角色）：")[1:]  # 跳过开头的介绍部分

    # 用于记录验证不通过的玩家
    problematic_sections = []

    for idx, player in enumerate(players, 1):
        # 补回开头的 "- 玩家名称（角色）："
        player_text = "- 玩家名称（角色）：" + player

        # 检查当前玩家是否符合格式
        if not player_pattern.match(player_text):
            problematic_sections.append((idx, player_text))

    return problematic_sections


def fix_format(content):
    """
    自动修复格式不符合的玩家分析部分。
    :param content: LLM 生成的文本内容
    :return: 修复后的内容
    """
    problematic_sections = validate_player_analysis(content)

    fixed_content = content
    for idx, section in problematic_sections:
        # 尝试修复
        lines = section.split("\n")
        fixed_section = []

        for line in lines:
            # 判断是否是分析部分的标题
            if re.match(r"^玩家名称（角色）：.*", line):
                fixed_section.append(line)
            elif re.match(r"^关键数据：", line):
                fixed_section.append("   - " + line)
            elif re.match(r"^问题分析：", line):
                fixed_section.append("   - " + line)
            elif re.match(r"^改进建议：", line):
                fixed_section.append("   - " + line)
            else:
                fixed_section.append("      " + line)

        # 替换原内容
        fixed_section_text = "\n".join(fixed_section)
        fixed_content = fixed_content.replace(section, fixed_section_text)

    return fixed_content


def fixes_format(content):
    problems = validate_player_analysis(content)

    if problems:
        print("以下玩家分析部分格式不符合要求：")
        for idx, section in problems:
            print(f"玩家 {idx}:\n{section}\n")

        print("正在尝试自动修复...")
        fixed_content = fix_format(content)
        print("修复后的内容：")
        print(fixed_content)
        return fixed_content
    else:
        print("所有玩家分析部分格式正确！")


if __name__ == "__main__":
    content = """
    ## 表现不佳玩家分析：
     - 玩家名称（角色）：匿名玩家（Bristleback 刚背兽）
      - 关键数据：2击杀，7死亡，8助攻，金钱获取499 GPM，经验获取1154 XPM，净值10880，英雄伤害10640，推塔伤害320
      - 问题分析：该玩家的死亡次数较高，导致其在战斗中无法有效生存，从而影响团队贡献。经济落后，未能充分发挥Bristleback作为坦克和持续输出者的潜力。出装问题在于选择了过多的防御装备（如Vanguard），而缺乏输出装来提高其伤害能力。
      - 改进建议：建议在出装上增加输出装备，例如Crimson Guard或Radiance，以提高团队战中的贡献。同时，减少不必要的死亡，增加团战中的生存时间。

    - 玩家名称（角色）：匿名玩家（Ogre Magi 食人魔魔法师）
      - 关键数据：3击杀，9死亡，7助攻，金钱获取1075 GPM，经验获取1529 XPM，净值24216，英雄伤害13329，推塔伤害650
      - 问题分析：该玩家死亡次数过高，影响了其在战斗中的持续输出能力。虽然经济和经验获取较高，但未能在关键时刻为团队提供足够的控制和辅助。出装偏向于生存和少量输出，缺乏足够的团队控制装备。
      - 改进建议：建议增加团队控制类装备，如Shiva's Guard或Glimmer Cape，以提高在团战中的生存和控制能力。注意站位，避免过早被击杀。

    - 玩家名称（角色）：匿名玩家（Phantom Lancer 幻影长矛手）
      - 关键数据：5击杀，5死亡，5助攻，金钱获取995 GPM，经验获取1228 XPM，净值21850，英雄伤害11159，推塔伤害1277
      - 问题分析：该玩家在击杀和助攻方面表现较好，但未能在关键团战中发挥决定性作用。出装偏向于切入和生存，缺乏爆发力和团队贡献。经济发展良好，但未能有效利用装备优势。
      - 改进建议：建议在出装上考虑增加Aghanim's Scepter或Butterfly，以提高其在团战中的爆发力和生存能力。加强与队友的配合，提高团战中切入的时机选择。
    """
    fixes_format(content)
