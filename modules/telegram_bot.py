import requests
import socket
import re
import zipfile
import tempfile
import os
import io
import html
class TelegramBot:
    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = f"https://api.telegram.org/bot{api_token}/"
        
        
    # def __convert_picture(self, image): base64 way
    #       #compress image
    #     decoded = base64.b64decode(image)send_message
    #     compressed_image  = Image.open(io.BytesIO(decoded)).convert("RGB")

        
    #     output_stream = io.BytesIO()
    #     compressed_image.save(output_stream, format="JPEG", optimize=True)
    #     compressed_image_data = output_stream.getvalue()

    #     return compressed_image_data


    #     return compressed_image_data
    def __send_telegrampicture(self, chat_id, message_id, image_data, caption=None):
        data = {
            "chat_id" : chat_id,
            "reply_to_message_id": message_id,
            "caption": caption,
        }
        
        files = {
            "photo": ("photo.jpg", io.BytesIO(image_data), "image/jpeg" )
        }
        
        url = self.base_url+"sendPhoto"
        print(f"Sent via {url} {data.keys()}")
        response = requests.post(url, data=data, files=files)
        response_parsed = response.json()
        
        if response_parsed["ok"]:
            print("Sent successfully")
        else:
            print(response_parsed["description"])
        
    def send_base64pictures(self, chat_id, message_id, base64_data, caption=None):
        """
        Sends an array of pictures of single picture

        Args:
            chat_id (string): chat id of chat in telegram
            message_id (string): message id for the chat in telegram
            base64_data (string or array): picture data in base64 encoded string
        """
        if isinstance(base64_data, list):
            for car in base64_data:
                # compressed_image = self.__convert_picture(image=car)
                self.__send_telegrampicture(chat_id=chat_id, image_data=car, message_id=message_id)
        elif isinstance(base64_data, str):
                # compressed_image = self.__convert_picture(image=base64_data)
                self.__send_telegrampicture(chat_id=chat_id, image_data=base64_data, message_id=message_id, caption=caption )
     
      
        # base64_compress_image = base64.b64encode(compressed_image_data)
        # print(base64_compress_image)
        #send the image


    def get_updates(self):
        get_updates_url = f"{self.base_url}getUpdates"
        try:
            response = requests.get(get_updates_url)
            response_json = response.json()
            
            if response_json["ok"]:
                updates = response_json["result"]
                if updates:
                    for key in updates:

                        if 'message' in key and 'chat' in key['message']:
                            chat = key['message']['chat']
                            chat_id = chat['id']
                            chat_title = chat.get('title', 'Private Chat')
                            chat_type = chat['type']
                            print(f"Chat ID: {chat_id}, Title: {chat_title}, Type: {chat_type}")
                            if 'text' in key['message']:
                                text = key['message']['text']
                                message_id = key['message']['message_id']
                                from_person = key['message']['from']['first_name']+ " " +  key['message']['from']['last_name']
                                print(f"Chat ID: {chat_id}, Title: {chat_title}, Type: {chat_type}")
                                print(f"Message: \"{text}\" MessageID:{message_id} From: {from_person} ")
                else:
                    print("Failed to get updates. Error:", response_json["description"], flush=True)
        except requests.exceptions.RequestException as e:
            print("Error getting updates:", e, flush=True)


    def get_recent_messages(self):
        get_updates_url = f"{self.base_url}getUpdates"
        try:
            response = requests.get(get_updates_url)
            response_json = response.json()
            
            if response_json["ok"]:
                updates = response_json["result"]
                if updates:
                    for key in updates:

                        if 'message' in key and 'chat' in key['message']:
                            chat = key['message']['chat']
                            chat_id = chat['id']
                            chat_title = chat.get('title', 'Private Chat')
                            chat_type = chat['type']
                            if 'text' in key['message']:
                                text = key['message']['text']
                                message_id = key['message']['message_id']
                                from_person = key['message']['from']['first_name']+ " " +  key['message']['from']['last_name']
                                print(f"Message: \"{text}\" MessageID: {message_id} From: {from_person} ChatID: {chat_id}")
                else:
                    print("Failed to get updates. Error:", response_json["description"], flush=True)
        except requests.exceptions.RequestException as e:
            print("Error getting updates:", e, flush=True)

    def send_message(self, chat_id, message, ParserType="Markdownv2", max_message_length=4096, MessageThreadID=None):
        send_message_url = f"{self.base_url}sendMessage"
        try:
            if len(message) <= max_message_length:
                # Message is within the length limit, send it as is
                data = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": ParserType,
                    "reply_to_message_id": MessageThreadID
                }
                response = requests.post(send_message_url, data=data)
                response_json = response.json()
                if response_json["ok"]:
                    print("Message sent successfully!", flush=True)
                else:
                    print("Failed to send message. Error:", response_json["description"], flush=True)
            else:
                # Message is too long, split it into chunks and send each chunk
                chunks = [message[i:i+max_message_length] for i in range(0, len(message), max_message_length)]
                for i, chunk in enumerate(chunks, start=1):
                    data = {
                        "chat_id": chat_id,
                        "text": chunk,
                        "parse_mode": ParserType,
                        "reply_to_message_id": MessageThreadID,
                    }
                    response = requests.post(send_message_url, data=data)
                    response_json = response.json()
                    if response_json["ok"]:
                        print(f"Chunk {i} sent successfully!", flush=True)
                    else:
                        print(f"Failed to send chunk {i}. Error:", response_json["description"], flush=True)
        except requests.exceptions.RequestException as e:
            print("Error sending message:", e, flush=True)

    def send_message_servername(self, chat_id, message, MessageThreadID):
        try: 
            get_computer_name = socket.gethostname()
            computer_name = re.sub(r'[^w\w\s]', '', get_computer_name)        
        except socket.error as e:
            return None
        message = f"From server: {computer_name} {message}"
        self.send_message(chat_id=chat_id, message=message, MessageThreadID=MessageThreadID)
    def send_dataframe_as_file(self, chat_id, dataframe, file_format="csv", caption="", file_name="data", MessageThreadID=None):
        if file_format not in ["csv", "xlsx"]:
            raise ValueError("Invalid file_format. Supported formats are 'csv' and 'xlsx'.")

        filename = f"{file_name}.{file_format}"
        if file_format == "csv":
            dataframe.to_csv(filename, index=False)
        elif file_format == "xlsx":
            dataframe.to_excel(filename, index=False)

        send_document_url = f"{self.base_url}sendDocument"
        files = {"document": open(filename, "rb")}

        try:
            response = requests.post(send_document_url, data={"chat_id": chat_id, "caption": caption, "reply_to_message_id": MessageThreadID}, files=files, )
            response_json = response.json()
            if response_json["ok"]:
                print("File sent successfully!", flush=True)
            else:
                print("Failed to send file. Error:", response_json["description"], flush=True)
        except requests.exceptions.RequestException as e:
            print("Error sending file:", e, flush=True)
        # finally:
        #     # Remove the temporary file
        #     import os
        #     os.remove(filename)
    def send_dataframe_as_csv_files(self, chat_id, dataframes, captions=None, file_names=None, MessageThreadID=None) :
        if not captions:
            captions = [""] * len(dataframes)
        if not file_names:
            file_names = ["data"] * len(dataframes)

        if len(dataframes) != len(captions) or len(dataframes) != len(file_names):
            raise ValueError("Length of dataframes, captions, and file_names should be the same.")

     #   try:
        for i, dataframe in enumerate(dataframes):
            file_name = f"{file_names[i]}.csv"
            file_path = os.path.join(tempfile.gettempdir(), file_name)

            dataframe.to_csv(file_path, index=False)

            send_document_url = f"{self.base_url}sendDocument"
            files = {"document": (file_name, open(file_path, "rb"))}
            caption = captions[i]

            try:
                response = requests.post(send_document_url, data={"chat_id": chat_id, "caption": caption, "reply_to_message_id": MessageThreadID}, files=files)
                response_json = response.json()
                if response_json["ok"]:
                    print(f"File '{file_name}' sent successfully!", flush=True)
                else:
                    print(f"Failed to send file '{file_name}'. Error:", response_json["description"], flush=True)
            except requests.exceptions.RequestException as e:
                print(f"Error sending file '{file_name}':", e, flush=True)
        # finally:
        #     # Remove the temporary CSV files
        #     for i in range(len(dataframes)):
        #         file_name = f"{file_names[i]}.csv"
        #         file_path = os.path.join(tempfile.gettempdir(), file_name)
        #         os.remove(file_path)

    
    def send_dataframe_as_multiple_files_as_zip(self, chat_id, dataframes, file_formats=None, captions=None, file_names=None, MessageThreadID=None):
        """
                # Example usage:
        # dataframes = [df1, df2]  # List of dataframes to send
        # file_formats = ["csv", "xlsx"]  # List of file formats corresponding to dataframes
        # captions = ["Caption 1", "Caption 2"]  # List of captions for files
        # file_names = ["data1", "data2"]  # List of file names
        # your_bot.send_dataframe_as_files(chat_id="your_chat_id_here", dataframes=dataframes, file_formats=file_formats, captions=captions, file_names=file_names)
        """
        if not file_formats:
            file_formats = ["csv"] * len(dataframes)
        if not captions:
            captions = [""] * len(dataframes)
        if not file_names:
            file_names = ["data"] * len(dataframes)

        if len(dataframes) != len(file_formats) or len(dataframes) != len(captions) or len(dataframes) != len(file_names):
            raise ValueError("Length of dataframes, file_formats, captions, and file_names should be the same.")

        # Create a temporary directory to store the individual files
        temp_dir = tempfile.mkdtemp()

        try:
            file_paths = []
            for i, dataframe in enumerate(dataframes):
                file_format = file_formats[i]
                file_name = f"{file_names[i]}.{file_format}"
                file_path = os.path.join(temp_dir, file_name)

                if file_format == "csv":
                    dataframe.to_csv(file_path, index=False)
                elif file_format == "xlsx":
                    dataframe.to_excel(file_path, index=False)

                file_paths.append(file_path)

            # Create a zip file containing all the individual files
            zip_filename = "data.zip"
            zip_file_path = os.path.join(temp_dir, zip_filename)
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for file_path in file_paths:
                    zipf.write(file_path, os.path.basename(file_path))

            send_document_url = f"{self.base_url}sendDocument"
            files = {"document": (zip_filename, open(zip_file_path, "rb"))}

            try:
                response = requests.post(send_document_url, data={"chat_id": chat_id, "reply_to_message_id": MessageThreadID}, files=files)
                response_json = response.json()
                if response_json["ok"]:
                    print("Files sent successfully!", flush=True)
                else:
                    print("Failed to send files. Error:", response_json["description"], flush=True)
            except requests.exceptions.RequestException as e:
                print("Error sending files:", e, flush=True)
        finally:
            # Remove the temporary directory and its contents
            for file_path in file_paths:
                os.remove(file_path)
            os.remove(zip_file_path)
            os.rmdir(temp_dir)

    def send_dataframe(self, chat_id, dataframe, exclude_columns=None, caption="", show_header=True, MessageThreadID=None):
        """
        Sends a DataFrame as a formatted message in Telegram, mimicking a table layout using monospaced fonts.
        Excludes specified columns from being included in the message.

        Parameters:
        - chat_id: The Telegram chat ID to send the message to.
        - dataframe: The pandas DataFrame to send.
        - exclude_columns: List of column names to exclude from the message.
        - caption: An optional caption for the message.
        - show_header: Whether to include the DataFrame's column headers.
        - MessageThreadID: Optional. The ID of the message thread to reply to.
        """
        if dataframe is None:
            print("Datafame empty nothing to send")
            return
        # Exclude specified columns if any
        if exclude_columns is not None:
            dataframe = dataframe.drop(columns=exclude_columns, errors='ignore')

        message_parts = [f"<b>{caption}</b>\n<pre>"] if caption else ["<pre>"]

        if show_header:
            # Add the header row, excluding the specified columns
            headers = [html.escape(str(col)) for col in dataframe.columns]
            header_row = " | ".join(headers)
            message_parts.append(header_row)

        # Adding a line separator between the header and data rows
        if show_header:
            message_parts.append('-' * len(header_row))

        for _, row in dataframe.iterrows():
            row_str = " | ".join([html.escape(str(cell)) for cell in row])
            message_parts.append(row_str)

        # Closing the <pre> tag
        message_parts.append("</pre>")

        message = "\n".join(message_parts)

        # Split and send the message if it exceeds Telegram's character limit
        max_length = 4096 - 10  # Subtracting some characters for safety margin
        if len(message) > max_length:
            # Ideally implement a more sophisticated splitting logic here
            print("Message exceeds the maximum length. Consider sending the DataFrame as a file or in multiple parts.")
        else:
            self.send_message(chat_id, message, ParserType="HTML", MessageThreadID=MessageThreadID)
   
    def send_href_formatted_dataframe(self, chat_id, dataframe, caption="", show_columns=None, show_header=False, MessageThreadID = None):
        # Format URLs using the provided code
        if 'HREF' in dataframe.columns:
                # Format titles as hyperlinks using the 'HREF' column
                hyperlink_column = dataframe.apply(lambda row: f'<a href="{row["HREF"]}">{row["Title"]}</a>', axis=1)
        else:
                # If there's no 'HREF' column, revert to displaying titles without hyperlink
            print("Warning: 'HREF' column not found. Titles will be displayed without hyperlinks.")
            hyperlink_column = dataframe['Title']
        # Create a copy of the DataFrame and sort it
        sorted_dataframe = dataframe.copy().drop(columns="HREF", errors='ignore')

        # Update the 'URL' column with hyperlinks
        sorted_dataframe['Title'] = hyperlink_column

        # Filter columns if specified

        # Convert the DataFrame to a formatted string with adjusted spacing
        header = sorted_dataframe.columns.to_list()
        formatted_rows = []

        # Format header
        if show_header == False:
            sorted_dataframe.columns = [None] * len(sorted_dataframe.columns) 
        else: #  show column names if show_header is true
            formatted_header = ' | '.join(header)
            formatted_rows.append(formatted_header)
        
           
        
        # Format data rows
        for _, row in sorted_dataframe.iterrows():
            formatted_row = ' | '.join(row.astype(str).values)
            formatted_rows.append(formatted_row)

        # Combine the caption and formatted DataFrame
        message = caption + "\n" + '\n'.join(formatted_rows)
        print(message)
        # Send the message
        self.send_message(chat_id, message, ParserType="HTML", MessageThreadID=MessageThreadID)
