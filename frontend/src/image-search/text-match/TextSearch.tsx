import {Textarea} from "@mantine/core";
import {useState} from "react";

export default function TextSearch() {
    const [text, setText] = useState('');

    return (
        <Textarea
            label="Search Text"
            placeholder="Describe the image you want to find..."
            minRows={4}
            value={text}
            miw={600}
            autosize
            onChange={(event) => setText(event.currentTarget.value)}
        />
    )
}