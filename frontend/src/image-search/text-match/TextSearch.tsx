import {rem, TextInput} from "@mantine/core";
import {isNotEmpty, useForm} from "@mantine/form";
import type {TextSearchRequest} from "../../models/TextSearchRequest.ts";
import styles from "./TextSearch.module.css";
import type ImageSearchContainerProps from "../ImageSearchContainerProps.ts";
import type {ImageMatchResult} from "../../models/ImageSearchResults.ts";

const TextSearch: React.FC<ImageSearchContainerProps> = ({setSearchResults}: ImageSearchContainerProps) => {
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
        try {
            const result = await fetch("http://localhost:8000/api/search/text", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // Important: Set the content type to JSON
                },
                body: JSON.stringify(formValues)
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
    };

    return (
        <form onSubmit={form.onSubmit(handleSubmit)}>
            <TextInput
                label="Search Text"
                placeholder="Describe the image you want to find..."
                classNames={{ wrapper: styles.searchField} }
                miw={600}
                mih={rem(120)}
                key={form.key('searchText')}
                {...form.getInputProps('searchText')}
            />
        </form>
    )
}

export default TextSearch;