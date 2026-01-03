import {rem, TextInput} from "@mantine/core";
import {isNotEmpty, useForm} from "@mantine/form";
import type {TextSearchRequest} from "../../models/TextSearchRequest.ts";
import styles from "./TextSearch.module.css";

export default function TextSearch() {
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
        // TODO make API call
        console.log(JSON.stringify(formValues, null, 2));
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