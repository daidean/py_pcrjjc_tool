from loguru import logger

from app.tool import Tool


def main():
    logger.info("Hello from py-pcrjjc-tool!")

    tool = Tool()

    query_text = "怎么拆 布丁 黄骑 毛二力 老师 蚊子"
    logger.info(query_text)

    chara_list = tool.parse_def(query_text)
    logger.info(chara_list)

    query_resp = tool.query(chara_list)
    logger.debug(query_resp)

    if query_resp["code"] == 0:
        results = query_resp["data"].get("result", [])
        atk_list = []
        for result in results:
            chara_list = [e["id"] for e in result["atk"]]
            atk_list.append(tool.parse_akt(chara_list))

        atk_maxlen = max([len(chara) for atk in atk_list for chara in atk])
        for atk in atk_list:
            logger.info("\t".join([f"{chara:<{atk_maxlen}}" for chara in atk]))

    else:
        logger.warning(f"查询异常 {query_resp}")
        return


if __name__ == "__main__":
    main()
