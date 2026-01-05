import {Group, SegmentedControl, Switch, Text, TextInput} from "@mantine/core";
import {isNotEmpty, useForm} from "@mantine/form";
import type {TextSearchRequest} from "../../models/TextSearchRequest.ts";
import styles from "./TextSearch.module.css";
import type ImageSearchContainerProps from "../ImageSearchContainerProps.ts";
import type {ImageMatchResult} from "../../models/ImageSearchResults.ts";
import {useState} from "react";

const TextSearch: React.FC<ImageSearchContainerProps> = ({setSearchResults, setLoading}: ImageSearchContainerProps) => {
    const [isMultimodal, setMultimodal] = useState(false)
    const [threshold, setThreshold] = useState("small")

    const form = useForm({
        mode: 'uncontrolled',
        initialValues: {
            searchText: ''
        },
        validate: {
            searchText: isNotEmpty('This field is required'),
        }
    });

    const handleSubmit = async (formValues: TextSearchRequest) => {
        setLoading(true);
        try {
            const result = await fetch("http://localhost:8000/api/search/text", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // Important: Set the content type to JSON
                },
                body: JSON.stringify({
                    searchText: formValues.searchText,
                    multimodal: isMultimodal,
                    threshold: threshold
                })
            });
            const data = (await result.json()) as ImageMatchResult[];
            setSearchResults({
                results: data
            });
        }
        catch (error) {
            console.error(error);
        }
        form.reset();
        setLoading(false);
    };

    return (
        <form onSubmit={form.onSubmit(handleSubmit)}>
            <TextInput
                label="Search Text"
                placeholder="Describe the image you want to find..."
                classNames={{ wrapper: styles.searchField} }
                key={form.key('searchText')}
                {...form.getInputProps('searchText')}
            />
            <Group styles={
                {
                    root: { paddingTop: '5px' }
                }}>
                <Text size={"sm"}><b>Distance Threshold:</b></Text>
                <SegmentedControl
                    color={"blue"}
                    value={threshold}
                    onChange={setThreshold}
                    data={[
                        { label: 'Small', value: 'small' },
                        { label: 'Medium', value: 'medium' },
                        { label: 'Large', value: 'yuge' }
                    ]}
                />
                <Switch
                    label="Multimodal Text Search"
                    withThumbIndicator={false}
                    onChange={(event) => setMultimodal(event.currentTarget.checked)}
                />
            </Group>
        </form>
    )
}

export default TextSearch;