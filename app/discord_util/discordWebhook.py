# system library for getting the command line argument
# web library
import http.client
import re

def split_message_by_double_newline(message, max_length=2000):
    """
    优先按照双换行符 (\n\n) 进行分段。
    如果某段仍超长，则进一步按单换行符 (\n) 或标点符号切割。
    """
    # 按双换行符分割
    paragraphs = message.split("\n\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        # 如果当前段加上新段落超过长度限制
        if len(current_chunk) + len(paragraph) + 2 > max_length:  # +2 是为了包括双换行符
            # 如果当前段已经有内容，保存
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""

        # 如果段落超过长度限制，进一步按单换行符或标点符号切割
        if len(paragraph) > max_length:
            split_chunks = split_message_by_newline_or_punctuation(paragraph, max_length)
            chunks.extend(split_chunks)
        else:
            current_chunk += paragraph + "\n\n"

    # 添加最后的段落
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def split_message_by_newline_or_punctuation(message, max_length):
    """
    智能分段，优先按单换行符 (\n) 切割，若仍超长则按标点符号切割。
    """
    # 按单换行符切割
    lines = message.split("\n")
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) + 1 > max_length:  # +1 是为了包括换行符
            # 如果当前段落超出长度限制
            if len(line) > max_length:
                # 超长行进一步按标点符号切割
                split_chunks = split_message_smart(line, max_length)
                chunks.extend(split_chunks)
            else:
                chunks.append(current_chunk.strip())
                current_chunk = ""

        current_chunk += line + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def split_message_smart(message, max_length):
    """
    最后一步：按句号、逗号等标点符号切割。
    """
    sentences = re.split(r"([。！？，])", message)  # 匹配句号、感叹号、问号、逗号
    chunks = []
    current_chunk = ""

    for i in range(0, len(sentences), 2):  # 每次取句子和标点
        sentence = sentences[i]
        if i + 1 < len(sentences):
            sentence += sentences[i + 1]  # 加上标点符号

        if len(current_chunk) + len(sentence) > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = ""

        current_chunk += sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def split_message_smart(message, max_length):
    """
    最后一步：按句号、逗号等标点符号切割。
    """
    sentences = re.split(r"([。！？，])", message)  # 匹配句号、感叹号、问号、逗号
    chunks = []
    current_chunk = ""

    for i in range(0, len(sentences), 2):  # 每次取句子和标点
        sentence = sentences[i]
        if i + 1 < len(sentences):
            sentence += sentences[i + 1]  # 加上标点符号

        if len(current_chunk) + len(sentence) > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = ""

        current_chunk += sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def send(message_list):
    # your webhook URL
    webhookurl = "https://discordapp.com/api/webhooks/1126626700583764039/bMgauGtsszaCd0_mGgMSc_KgZ9MQIiNF1grrliESymBztocLBMOtZsZ_-oZZya6H9Niu"
    results = []
    header = "========================================================= GG_CHATALYZE ============================================================="

    # 包含 header 并自动分段
    new_message_list = [header] + message_list
    final_message_list = []
    for message in new_message_list:
        final_message_list.extend(split_message_by_double_newline(message, max_length=2000))

    for message in final_message_list:
        # compile the form data (BOUNDARY can be anything)
        formdata = (
            "------:::BOUNDARY:::\r\n"
            "Content-Disposition: form-data; name=\"content\"\r\n\r\n"
            + message
            + "\r\n------:::BOUNDARY:::--"
        ).encode("utf-8")
        # get the connection and make the request
        connection = http.client.HTTPSConnection("discordapp.com")
        connection.request("POST", webhookurl, formdata, {
            'content-type': "multipart/form-data; boundary=----:::BOUNDARY:::",
            'cache-control': "no-cache",
        })

        # get the response
        response = connection.getresponse()
        results.append(response.read().decode("utf-8"))

    # return back to the calling function with the result
    return results